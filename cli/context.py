"""
Codebase context management and retrieval
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib
import ast
import re
from dataclasses import dataclass

# Vector search imports
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Code parsing imports
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


# Global cache for embedding model and ChromaDB
_embedding_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.Client] = None
_parser: Optional[Parser] = None


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata"""
    file_path: str
    content: str
    chunk_type: str  # 'function', 'class', 'file', 'import'
    name: str
    start_line: int
    end_line: int
    imports: List[str]  # Files this chunk depends on


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model (singleton)"""
    global _embedding_model
    if _embedding_model is None:
        # Use a lightweight, fast model for code embeddings
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def get_chroma_client(context_dir: str) -> chromadb.Client:
    """Get or initialize ChromaDB client (singleton)"""
    global _chroma_client
    if _chroma_client is None:
        # Store ChromaDB data in a hidden folder
        db_path = os.path.join(context_dir, ".code_assistant_db")
        os.makedirs(db_path, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
    return _chroma_client


def get_parser() -> Parser:
    """Get or initialize tree-sitter parser (singleton)"""
    global _parser
    if _parser is None:
        PY_LANGUAGE = Language(tspython.language())
        _parser = Parser(PY_LANGUAGE)
    return _parser


def extract_imports(code: str) -> List[str]:
    """Extract import statements from Python code"""
    imports = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except:
        pass
    return imports


def parse_file_with_treesitter(file_path: str) -> List[CodeChunk]:
    """Parse a Python file and extract functions, classes, and imports"""
    chunks = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Get imports
        imports = extract_imports(code)

        # Parse with tree-sitter
        parser = get_parser()
        tree = parser.parse(bytes(code, 'utf8'))
        root_node = tree.root_node

        def extract_node_text(node) -> str:
            return code[node.start_byte:node.end_byte]

        # Extract top-level definitions
        for child in root_node.children:
            if child.type == 'function_definition':
                name_node = child.child_by_field_name('name')
                if name_node:
                    name = extract_node_text(name_node)
                    content = extract_node_text(child)
                    chunks.append(CodeChunk(
                        file_path=file_path,
                        content=content,
                        chunk_type='function',
                        name=name,
                        start_line=child.start_point[0],
                        end_line=child.end_point[0],
                        imports=imports
                    ))

            elif child.type == 'class_definition':
                name_node = child.child_by_field_name('name')
                if name_node:
                    name = extract_node_text(name_node)
                    content = extract_node_text(child)
                    chunks.append(CodeChunk(
                        file_path=file_path,
                        content=content,
                        chunk_type='class',
                        name=name,
                        start_line=child.start_point[0],
                        end_line=child.end_point[0],
                        imports=imports
                    ))

        # If no functions/classes found, add whole file as chunk
        if not chunks:
            chunks.append(CodeChunk(
                file_path=file_path,
                content=code[:5000],  # Limit size
                chunk_type='file',
                name=os.path.basename(file_path),
                start_line=0,
                end_line=len(code.split('\n')),
                imports=imports
            ))

    except Exception as e:
        # Fallback: return file as single chunk
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()[:5000]
            chunks.append(CodeChunk(
                file_path=file_path,
                content=content,
                chunk_type='file',
                name=os.path.basename(file_path),
                start_line=0,
                end_line=len(content.split('\n')),
                imports=[]
            ))
        except:
            pass

    return chunks


def infer_target_files(query: str, context_dir: str) -> List[str]:
    """Infer which files the user wants to create/edit based on query"""
    target_files = []

    # Pattern 1: Explicit file mentions
    # "create calc.py", "edit utils/helper.py", "modify config.json"
    file_patterns = [
        r'create\s+([a-zA-Z0-9_./]+\.[a-zA-Z0-9]+)',
        r'edit\s+([a-zA-Z0-9_./]+\.[a-zA-Z0-9]+)',
        r'modify\s+([a-zA-Z0-9_./]+\.[a-zA-Z0-9]+)',
        r'update\s+([a-zA-Z0-9_./]+\.[a-zA-Z0-9]+)',
        r'in\s+([a-zA-Z0-9_./]+\.[a-zA-Z0-9]+)',
        r'file\s+([a-zA-Z0-9_./]+\.[a-zA-Z0-9]+)',
    ]

    for pattern in file_patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        target_files.extend(matches)

    # Pattern 2: Infer from context
    # "add a calculator" -> might create calc.py or calculator.py
    # "add authentication" -> might create auth.py or authentication.py
    keywords_to_files = {
        r'\bcalculator\b': ['calc.py', 'calculator.py'],
        r'\bauth(?:entication)?\b': ['auth.py', 'authentication.py'],
        r'\bconfig(?:uration)?\b': ['config.py', 'settings.py'],
        r'\butils?\b': ['utils.py', 'helpers.py'],
        r'\btest(?:s)?\b': ['test.py', 'tests.py'],
        r'\bmodel(?:s)?\b': ['model.py', 'models.py'],
        r'\bview(?:s)?\b': ['view.py', 'views.py'],
        r'\bapi\b': ['api.py', 'routes.py'],
        r'\bdatabase\b': ['database.py', 'db.py'],
    }

    query_lower = query.lower()
    for pattern, candidates in keywords_to_files.items():
        if re.search(pattern, query_lower):
            # Check which candidate files exist
            for candidate in candidates:
                full_path = os.path.join(context_dir, candidate)
                if os.path.exists(full_path):
                    target_files.append(candidate)
                    break

    return list(set(target_files))  # Remove duplicates


def get_relevant_context(query: str, context_dir: str, max_chunks: int = 5) -> str:
    """
    Get relevant code context using semantic search.

    This now uses:
    - Vector embeddings (ChromaDB + sentence-transformers)
    - Tree-sitter parsing for code structure
    - Smart file selection based on query intent
    """

    # Get or create collection
    client = get_chroma_client(context_dir)
    collection_name = "codebase"

    try:
        collection = client.get_collection(collection_name)
    except:
        # Collection doesn't exist, index first
        collection = index_codebase(context_dir)

    # Infer target files from query
    target_files = infer_target_files(query, context_dir)

    # Perform semantic search
    model = get_embedding_model()
    query_embedding = model.encode([query])[0].tolist()

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=max_chunks,
        )

        # Build context from results
        context_parts = []

        # Add inferred target files context if available
        if target_files:
            context_parts.append("# IMPORTANT: Inferred target files for this query:")
            context_parts.append("# When creating/editing files, use these EXACT paths (preserve subdirectories):")
            for tf in target_files:
                context_parts.append(f"#   - {tf}")
            context_parts.append("#")
            context_parts.append("# Use format: ```python:{exact_filename_with_path}")
            context_parts.append("")

        # Add semantic search results
        if results['documents'] and results['documents'][0]:
            context_parts.append("# Relevant code from codebase:\n")

            for idx, (doc, metadata) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0]
            )):
                file_path = metadata.get('file_path', 'unknown')
                chunk_type = metadata.get('chunk_type', 'code')
                name = metadata.get('name', '')

                rel_path = os.path.relpath(file_path, context_dir)

                if name:
                    context_parts.append(f"# {chunk_type.capitalize()}: {name} ({rel_path})")
                else:
                    context_parts.append(f"# File: {rel_path}")

                context_parts.append(doc)
                context_parts.append("")

        return "\n".join(context_parts)

    except Exception as e:
        # Fallback to simple file-based context
        return get_simple_context(query, context_dir, max_chunks)


def get_simple_context(query: str, context_dir: str, max_files: int = 3) -> str:
    """Fallback: simple context retrieval without vector search"""
    context_path = Path(context_dir)
    python_files = list(context_path.rglob("*.py"))

    ignore_patterns = [
        "__pycache__", ".venv", "venv", ".git",
        "node_modules", ".pytest_cache", ".mypy_cache",
    ]

    filtered_files = [
        f for f in python_files
        if not any(pattern in str(f) for pattern in ignore_patterns)
    ]

    filtered_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    selected_files = filtered_files[:max_files]

    context_parts = []
    for file in selected_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()

            if len(content) > 5000:
                content = content[:5000] + "\n\n# ... (truncated)"

            relative_path = file.relative_to(context_path)
            context_parts.append(f"# File: {relative_path}\n{content}")
        except:
            continue

    return "\n\n---\n\n".join(context_parts)


def index_codebase(context_dir: str):
    """
    Index a codebase using vector embeddings and tree-sitter parsing.

    Returns ChromaDB collection with indexed code chunks.
    """

    context_path = Path(context_dir)

    # Find all Python files
    python_files = list(context_path.rglob("*.py"))

    # Filter ignored paths
    ignore_patterns = [
        "__pycache__", ".venv", "venv", ".git",
        "node_modules", ".pytest_cache", ".mypy_cache",
        ".code_assistant_db",
    ]

    filtered_files = [
        f for f in python_files
        if not any(pattern in str(f) for pattern in ignore_patterns)
    ]

    # Get ChromaDB client and create/reset collection
    client = get_chroma_client(context_dir)
    collection_name = "codebase"

    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name)
    except:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Get embedding model
    model = get_embedding_model()

    # Parse and index all files
    total_chunks = 0
    all_chunks = []
    all_embeddings = []
    all_ids = []
    all_metadatas = []

    for file_path in filtered_files:
        # Parse file into chunks
        chunks = parse_file_with_treesitter(str(file_path))

        for chunk_idx, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{file_path}:{chunk.start_line}:{chunk_idx}"

            # Generate embedding
            embedding = model.encode([chunk.content])[0].tolist()

            # Prepare metadata
            metadata = {
                "file_path": str(file_path),
                "chunk_type": chunk.chunk_type,
                "name": chunk.name,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "imports": ",".join(chunk.imports),
            }

            all_chunks.append(chunk.content)
            all_embeddings.append(embedding)
            all_ids.append(chunk_id)
            all_metadatas.append(metadata)
            total_chunks += 1

    # Add to ChromaDB in batch
    if all_chunks:
        collection.add(
            embeddings=all_embeddings,
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadatas,
        )

    return collection


def search_codebase(query: str, context_dir: str, max_results: int = 10) -> List[Dict]:
    """
    Search codebase using semantic similarity and keyword matching.
    """

    # Get or create collection
    client = get_chroma_client(context_dir)
    collection_name = "codebase"

    try:
        collection = client.get_collection(collection_name)
    except:
        # Index if not already done
        collection = index_codebase(context_dir)

    # Perform semantic search
    model = get_embedding_model()
    query_embedding = model.encode([query])[0].tolist()

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
        )

        search_results = []
        if results['documents'] and results['documents'][0]:
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                search_results.append({
                    "file": metadata.get('file_path', ''),
                    "chunk_type": metadata.get('chunk_type', ''),
                    "name": metadata.get('name', ''),
                    "content": doc,
                    "start_line": metadata.get('start_line', 0),
                })

        return search_results

    except Exception as e:
        # Fallback to simple keyword search
        results = []
        context_path = Path(context_dir)
        python_files = list(context_path.rglob("*.py"))

        for file in python_files[:max_results]:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()

                if query.lower() in content.lower():
                    results.append({
                        "file": str(file),
                        "matches": content.count(query.lower()),
                    })
            except:
                continue

        return results


def build_file_dependency_graph(context_dir: str) -> Dict[str, List[str]]:
    """
    Build a graph of file dependencies based on imports.

    Returns: dict mapping file paths to list of files they import from
    """
    context_path = Path(context_dir)
    python_files = list(context_path.rglob("*.py"))

    ignore_patterns = [
        "__pycache__", ".venv", "venv", ".git",
        "node_modules", ".pytest_cache", ".mypy_cache",
    ]

    filtered_files = [
        f for f in python_files
        if not any(pattern in str(f) for pattern in ignore_patterns)
    ]

    dependency_graph = {}

    # Build mapping of module names to file paths
    module_to_file = {}
    for file_path in filtered_files:
        rel_path = file_path.relative_to(context_path)
        module_name = str(rel_path).replace('.py', '').replace('/', '.')
        module_to_file[module_name] = str(file_path)

    # Extract imports and build graph
    for file_path in filtered_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            imports = extract_imports(code)
            dependencies = []

            for imp in imports:
                # Try to resolve to local files
                if imp in module_to_file:
                    dependencies.append(module_to_file[imp])

            dependency_graph[str(file_path)] = dependencies

        except:
            dependency_graph[str(file_path)] = []

    return dependency_graph
