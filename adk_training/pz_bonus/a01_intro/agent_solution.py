"""
Moduł A01: Wprowadzenie do ADK - ROZWIĄZANIA ĆWICZEŃ
====================================================
Ćwiczenia:
1. Dodaj parametr number_of_images - generowanie wielu obrazów
2. Dodaj narzędzie delete_artifact() - usuwanie plików
3. Dodaj walidację promptu - sprawdzanie przed generowaniem
"""

import os
from dotenv import load_dotenv
from google.genai import types, Client
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext, FunctionTool, load_artifacts

load_dotenv()

MODEL = "gemini-2.0-flash-001"
AGENT_APP_NAME = 'artistagent_solution'

client = Client()

# =============================================================================
# ĆWICZENIE 1: GENEROWANIE WIELU OBRAZÓW
# =============================================================================

async def generate_images(prompt: str, tool_context: 'ToolContext', count: int = 1):
    """
    Generuje wiele obrazów na podstawie promptu.

    IMPORTANT: Pass the user's prompt EXACTLY as provided. Do NOT modify or expand it.
    The function validates: minimum 10 characters, no forbidden words (violence, weapon, blood).

    Args:
        prompt: Opis obrazu do wygenerowania (EXACT user input, minimum 10 characters)
        count: Liczba obrazów do wygenerowania (1-4)
    """
    # Walidacja liczby obrazów
    if count < 1 or count > 4:
        return {
            'status': 'failed',
            'detail': 'Count must be between 1 and 4'
        }

    # Walidacja promptu (Ćwiczenie 3)
    if len(prompt) < 10:
        return {
            'status': 'failed',
            'detail': 'Prompt too short (minimum 10 characters)'
        }

    # Lista zabronionych słów (przykład)
    forbidden_words = ['violence', 'weapon', 'blood']
    if any(word in prompt.lower() for word in forbidden_words):
        return {
            'status': 'failed',
            'detail': 'Prompt contains forbidden content'
        }

    try:
        # Generuj obrazy
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config={'number_of_images': count},
        )

        if not response.generated_images:
            return {'status': 'failed', 'detail': 'No images generated'}

        # Zapisz wszystkie obrazy
        saved_files = []
        for i, img in enumerate(response.generated_images):
            image_bytes = img.image.image_bytes
            filename = f'image_{i+1}.png' if count > 1 else 'image.png'

            await tool_context.save_artifact(
                f'user:{filename}',
                types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
            )
            saved_files.append(filename)

        return {
            'status': 'success',
            'detail': f'Generated {len(saved_files)} image(s) successfully',
            'files': saved_files
        }

    except Exception as e:
        return {
            'status': 'failed',
            'detail': f'Error generating images: {str(e)}'
        }

# =============================================================================
# ĆWICZENIE 2: USUWANIE ARTEFAKTÓW
# =============================================================================

async def delete_artifact(filename: str, tool_context: ToolContext) -> dict:
    """
    Usuwa plik z artifact service.

    Args:
        filename: Nazwa pliku do usunięcia (bez prefiksu 'user:')
    """
    try:
        # Sprawdź czy plik istnieje
        available_files = await tool_context.list_artifacts()

        # list_artifacts() zwraca nazwy Z prefiksem 'user:', więc musimy dodać prefix do porównania
        full_filename = f'user:{filename}'

        if full_filename not in available_files:
            # Usuń prefix 'user:' z nazw dla czytelności w komunikacie
            clean_files = [f.replace('user:', '') for f in available_files]
            return {
                'status': 'failed',
                'detail': f'File "{filename}" not found. Available files: {", ".join(clean_files)}'
            }

        # Usuń plik - używamy pełnej nazwy z prefiksem
        await tool_context.delete_artifact(full_filename)

        return {
            'status': 'success',
            'detail': f'File "{filename}" deleted successfully'
        }

    except Exception as e:
        return {
            'status': 'failed',
            'detail': f'Error deleting file: {str(e)}'
        }

# =============================================================================
# NARZĘDZIE: LISTA PLIKÓW
# =============================================================================

async def list_user_files(tool_context: ToolContext) -> str:
    """Wyświetla listę dostępnych plików użytkownika."""
    try:
        available_files = await tool_context.list_artifacts()

        if not available_files:
            return "📭 You have no saved files."

        # Usuń prefix 'user:' z nazw dla czytelności
        clean_files = [f.replace('user:', '') for f in available_files]
        file_list = "\n".join([f"  📄 {fname}" for fname in clean_files])
        return f"📁 Your files ({len(clean_files)}):\n{file_list}"

    except Exception as e:
        return f"❌ Error listing files: {str(e)}"

# =============================================================================
# AGENT Z WSZYSTKIMI ROZWIĄZANIAMI
# =============================================================================

root_agent = LlmAgent(
    name=AGENT_APP_NAME,
    model=MODEL,
    description="An agent that generates images using Imagen 3.0 and manages artifacts.",
    instruction="""You are an AI artist assistant.

AVAILABLE TOOLS:
1. generate_images(prompt, count) - Generate 1-4 images based on description
2. delete_artifact(filename) - Delete a saved file
3. list_user_files() - Show all saved files
4. load_artifacts() - Load and display saved images

GUIDELINES:
- CRITICAL: Pass the user's prompt EXACTLY as they provided it to generate_images()
- Do NOT modify, expand, or improve the prompt before calling the tool
- BEFORE calling generate_images(), check if the user's prompt is at least 10 characters long
- If the prompt is too short (< 10 chars), tell the user: "Your prompt is too short. Please provide at least 10 characters."
- If the prompt contains forbidden words (violence, weapon, blood), reject it immediately
- Only call generate_images() if the prompt passes these checks
- Inform users about saved files
- Help manage their artifact library

Be helpful but respect the user's exact input!
""",
    tools=[
        generate_images,
        delete_artifact,
        list_user_files,
        load_artifacts,
    ],
)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE:

1. Ćwiczenie 1 - Wiele obrazów:
   "Generate 3 images of a sunset over the ocean"
   "Wygeneruj 2 obrazy kota na kanapie"

2. Ćwiczenie 2 - Usuwanie:
   "List my files"
   "Delete image_2.png"
   "List my files again"

3. Ćwiczenie 3 - Walidacja:
   "Generate image of cat" (za krótki prompt - błąd)
   "Generate image of a beautiful cat sitting on a couch" (OK)
   "Generate image with violence" (zabronione słowo - błąd)

4. Kompleksowy scenariusz:
   "Generate 3 images of mountains"
   "List my files"
   "Delete image_1.png"
   "Load the remaining images"

URUCHOMIENIE:
adk web
"""

