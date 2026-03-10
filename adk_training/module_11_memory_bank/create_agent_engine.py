"""
Script to create an Agent Engine instance with Memory Bank for ADK.

This script creates an Agent Engine with Memory Bank configuration
in Vertex AI. The Agent Engine ID will be used by your ADK agent
to access Memory Bank services.

Usage:
    python create_agent_engine.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import vertexai
except ImportError:
    print("❌ Error: vertexai package not installed")
    print("   Run: pip install google-cloud-aiplatform")
    sys.exit(1)

# Get configuration from environment
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Memory Bank models
# Using gemini-1.5-flash for better stability and higher rate limits
MEMORY_GENERATION_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "text-embedding-005"

if not PROJECT_ID:
    print("❌ Error: GOOGLE_CLOUD_PROJECT not set in .env file")
    print("   Please copy .env.template to .env and fill in your project ID")
    sys.exit(1)

print("=" * 70)
print("🚀 CREATING AGENT ENGINE WITH MEMORY BANK")
print("=" * 70)
print(f"\n📋 Configuration:")
print(f"   Project ID: {PROJECT_ID}")
print(f"   Location: {LOCATION}")
print(f"   Memory Generation Model: {MEMORY_GENERATION_MODEL}")
print(f"   Embedding Model: {EMBEDDING_MODEL}")
print(f"\n⏳ Creating Agent Engine (this may take a minute)...\n")

try:
    # Initialize Vertex AI client
    client = vertexai.Client(
        project=PROJECT_ID,
        location=LOCATION
    )

    # Create Agent Engine with Memory Bank configuration
    agent_engine = client.agent_engines.create(
        config={
            "displayName": "ADK Agent Engine with Memory Bank PZ",
            "contextSpec": {
                "memoryBankConfig": {
                    "generationConfig": {
                        "model": f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MEMORY_GENERATION_MODEL}"
                    },
                    "similaritySearchConfig": {
                        "embeddingModel": f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{EMBEDDING_MODEL}"
                    }
                }
            }
        }
    )

    # Extract Agent Engine ID from resource name
    # Format: projects/PROJECT/locations/LOCATION/reasoningEngines/ID
    resource_name = agent_engine.api_resource.name
    agent_engine_id = resource_name.split("/")[-1]

    print("=" * 70)
    print("✅ AGENT ENGINE CREATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📝 Resource Details:")
    print(f"   Full Resource Name: {resource_name}")
    print(f"   Agent Engine ID: {agent_engine_id}")
    print(f"   Project: {PROJECT_ID}")
    print(f"   Location: {LOCATION}")

    print(f"\n🔧 Next Steps:")
    print(f"   1. Copy the Agent Engine ID above")
    print(f"   2. Add it to your .env file:")
    print(f"      AGENT_ENGINE_ID={agent_engine_id}")
    print(f"   3. Test connection: python test_connection.py")
    print(f"   4. Run the agent: adk web")

    print(f"\n💡 To view in GCP Console:")
    print(f"   https://console.cloud.google.com/vertex-ai/agent-builder")

    print(f"\n📌 Note:")
    print(f"   This Agent Engine provides Memory Bank infrastructure.")
    print(f"   Your ADK agent (agent.py) will use this Agent Engine ID")
    print(f"   to store and retrieve memories across sessions.")
    print()

except Exception as e:
    print("=" * 70)
    print("❌ ERROR CREATING AGENT ENGINE")
    print("=" * 70)
    print(f"\nError: {e}")
    print(f"\n🔍 Troubleshooting:")
    print(f"   1. Check if Vertex AI API is enabled:")
    print(f"      gcloud services enable aiplatform.googleapis.com")
    print(f"   2. Verify authentication:")
    print(f"      gcloud auth application-default login")
    print(f"   3. Check project permissions:")
    print(f"      gcloud projects get-iam-policy {PROJECT_ID}")
    print(f"   4. Verify project ID is correct:")
    print(f"      gcloud config get-value project")
    print(f"   5. Make sure you have the required IAM roles:")
    print(f"      - Vertex AI User (roles/aiplatform.user)")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

