"""
Moduł A03: Autoimport Files to Artifact Service - ROZWIĄZANIA ĆWICZEŃ
=====================================================================
Ćwiczenia:
1. Dodaj list_artifacts_with_metadata() - lista plików z metadanymi
2. Dodaj filtrowanie po typie pliku - tylko obrazy/PDF/etc
3. Dodaj automatyczną analizę po uploadzie - callback
"""

import os
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts, ToolContext
from google.adk.apps import App
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin

load_dotenv()

MODEL = "gemini-2.5-flash"
AGENT_APP_NAME = 'artifact_manager_solution'

# =============================================================================
# ĆWICZENIE 1: LISTA PLIKÓW Z METADANYMI
# =============================================================================

async def list_artifacts_with_metadata(tool_context: ToolContext) -> str:
    """
    Wyświetla listę plików z metadanymi (typ, rozmiar).
    """
    try:
        files = await tool_context.list_artifacts()
        
        if not files:
            return "📭 No files uploaded yet."
        
        result = f"📁 Your files ({len(files)}):\n\n"
        
        for filename in files:
            try:
                # Załaduj artifact aby uzyskać metadata
                artifact = await tool_context.load_artifact(f'user:{filename}')
                
                # Pobierz informacje
                mime_type = getattr(artifact, 'mime_type', 'unknown')
                
                # Określ ikonę na podstawie typu
                if mime_type.startswith('image/'):
                    icon = '🖼️'
                elif mime_type == 'application/pdf':
                    icon = '📄'
                elif mime_type.startswith('text/'):
                    icon = '📝'
                else:
                    icon = '📦'
                
                result += f"{icon} {filename}\n"
                result += f"   Type: {mime_type}\n\n"
            
            except Exception as e:
                result += f"❌ {filename} (error loading metadata)\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"

# =============================================================================
# ĆWICZENIE 2: FILTROWANIE PO TYPIE PLIKU
# =============================================================================

async def list_artifacts_by_type(file_type: str, tool_context: ToolContext) -> str:
    """
    Filtruje pliki po typie MIME.
    
    Args:
        file_type: Typ pliku ('image', 'pdf', 'text', 'all')
    """
    try:
        files = await tool_context.list_artifacts()
        
        if not files:
            return "📭 No files uploaded yet."
        
        # Mapowanie typów
        type_mapping = {
            'image': 'image/',
            'pdf': 'application/pdf',
            'text': 'text/',
            'all': ''
        }
        
        filter_prefix = type_mapping.get(file_type.lower(), '')
        
        # Filtruj pliki
        filtered_files = []
        for filename in files:
            try:
                artifact = await tool_context.load_artifact(f'user:{filename}')
                mime_type = getattr(artifact, 'mime_type', '')
                
                if filter_prefix == '' or mime_type.startswith(filter_prefix):
                    filtered_files.append((filename, mime_type))
            except:
                continue
        
        if not filtered_files:
            return f"📭 No {file_type} files found."
        
        result = f"📁 {file_type.upper()} files ({len(filtered_files)}):\n\n"
        for filename, mime_type in filtered_files:
            icon = '🖼️' if mime_type.startswith('image/') else '📄'
            result += f"{icon} {filename} ({mime_type})\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error filtering files: {str(e)}"

# =============================================================================
# ĆWICZENIE 3: AUTOMATYCZNA ANALIZA PO UPLOADZIE
# =============================================================================

async def analyze_uploaded_file(filename: str, tool_context: ToolContext) -> str:
    """
    Analizuje uploadowany plik (symulacja - w prawdziwej implementacji
    użyj Vision API dla obrazów, Document AI dla PDF, etc.)
    """
    try:
        artifact = await tool_context.load_artifact(f'user:{filename}')
        mime_type = getattr(artifact, 'mime_type', 'unknown')
        
        # Symulacja analizy
        if mime_type.startswith('image/'):
            analysis = f"""
🖼️ IMAGE ANALYSIS: {filename}

Type: {mime_type}
Status: ✅ Successfully uploaded

Suggested actions:
- Use Vision API for detailed analysis
- Extract text with OCR
- Detect objects and labels
- Generate image description

To analyze, ask: "Analyze the image in detail"
"""
        
        elif mime_type == 'application/pdf':
            analysis = f"""
📄 PDF ANALYSIS: {filename}

Type: {mime_type}
Status: ✅ Successfully uploaded

Suggested actions:
- Extract text with Document AI
- Parse tables and forms
- Generate summary
- Search for keywords

To analyze, ask: "Extract text from the PDF"
"""
        
        else:
            analysis = f"""
📦 FILE UPLOADED: {filename}

Type: {mime_type}
Status: ✅ Successfully uploaded

File is ready for processing.
"""
        
        return analysis
    
    except Exception as e:
        return f"❌ Error analyzing file: {str(e)}"

# =============================================================================
# AGENT Z WSZYSTKIMI ROZWIĄZANIAMI
# =============================================================================

root_agent = LlmAgent(
    name=AGENT_APP_NAME,
    model=MODEL,
    description="An agent that manages uploaded files with advanced features.",
    instruction="""You are a file management assistant.

AVAILABLE TOOLS:
1. load_artifacts() - Load and display uploaded files
2. list_artifacts_with_metadata() - Show files with type and metadata
3. list_artifacts_by_type(file_type) - Filter files by type ('image', 'pdf', 'text', 'all')
4. analyze_uploaded_file(filename) - Analyze a specific file

WORKFLOW:
1. When user uploads a file, automatically call analyze_uploaded_file()
2. Suggest relevant actions based on file type
3. Help user manage their file library

GUIDELINES:
- Be proactive - suggest what user can do with uploaded files
- Explain file types and capabilities
- Help organize and filter files

Be helpful and informative!
""",
    tools=[
        load_artifacts,
        list_artifacts_with_metadata,
        list_artifacts_by_type,
        analyze_uploaded_file,
    ],
)

# Aplikacja z pluginem auto-importu
app = App(
    name='a03_autoimport_files_to_artifact_service',
    root_agent=root_agent,
    plugins=[SaveFilesAsArtifactsPlugin()],
)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE:

1. Ćwiczenie 1 - Metadata:
   - Upload kilka plików (obraz, PDF, txt)
   - "Show my files with details"
   - "List all artifacts with metadata"

2. Ćwiczenie 2 - Filtrowanie:
   - "Show only images"
   - "List PDF files"
   - "Show all text files"

3. Ćwiczenie 3 - Analiza:
   - Upload obraz
   - "Analyze the uploaded image"
   - Upload PDF
   - "Analyze the PDF file"

4. Kompleksowy scenariusz:
   - Upload 3 obrazy, 2 PDF, 1 txt
   - "Show all my files"
   - "Filter only images"
   - "Analyze image_1.png"
   - "What can I do with these files?"

URUCHOMIENIE:
adk web

UWAGA:
Plugin SaveFilesAsArtifactsPlugin automatycznie importuje pliki
uploadowane przez drag & drop w interfejsie!
"""

