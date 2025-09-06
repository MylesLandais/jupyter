# initialize_runpod_ollama.py
import os
import runpod
import time
import json
from dotenv import load_dotenv

# Load environment variables from.env file (e.g., RUNPOD_API_KEY, RUNPOD_NETWORK_VOLUME_ID)
load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
if not RUNPOD_API_KEY:
    raise ValueError("RUNPOD_API_KEY environment variable not set. Please set it in your.env file or environment.")
runpod.api_key = RUNPOD_API_KEY

# --- Configuration for the Pod ---
POD_NAME_PREFIX = "Nebula_Ollama" # Prefix for easy identification
# Your custom Docker Hub image with the pre-pulling entrypoint (e.g., from Section 3.3)
OLLAMA_IMAGE = "ollama/ollama:latest"
GPU_TYPE = "NVIDIA GeForce RTX 3090" # As requested by user
GPU_COUNT = 1
CONTAINER_DISK_SIZE_GB = 64 # Allocate sufficient disk for image and potential temporary data
# Optional: ID of a pre-created RunPod Network Volume for persistent model storage
NETWORK_VOLUME_ID = os.getenv("RUNPOD_NETWORK_VOLUME_ID")
# Set the model to be pulled by the custom entrypoint script
OLLAMA_MODEL_TO_PULL = "mistral-small3.2:latest" # Example model

def create_ollama_pod(pod_name, image_name, gpu_type, gpu_count, disk_size, network_volume_id=None, ollama_model=None):
    """
    Creates a RunPod GPU Pod for Ollama with specified configurations.
    """
    print(f"Attempting to create RunPod with name: {pod_name} and GPU: {gpu_type}...")
    try:
        pod_config = {
            "name": pod_name,
            "image_name": image_name,
            "gpu_type_id": gpu_type,
            "gpu_count": gpu_count,
            "volume_in_gb": disk_size,
            "ports": "11434/http",
            # Changed env format to dictionary as expected by the API
            "env": {
                "OLLAMA_HOST": "0.0.0.0",
                "OLLAMA_MODEL": ollama_model if ollama_model else "",
                "OLLAMA_KEEP_ALIVE": "24h"
            }
        }

        if network_volume_id:
            pod_config["network_volume_id"] = network_volume_id
            pod_config["volume_mount_path"] = "/root/.ollama"  # Mount path for the network volume

        pod = runpod.create_pod(**pod_config)
        print(f"Pod creation initiated. Pod ID: {pod['id']}, Status: {pod}")
        return pod
    except runpod.error.QueryError as e:
        print(f"Error creating pod: {e}")
        return None

def main():
    # Generate a unique pod name for this session using a timestamp
    timestamp = int(time.time())
    pod_name = f"{POD_NAME_PREFIX}-{timestamp}"

    # Create the Ollama Pod
    pod = create_ollama_pod(
        pod_name,
        OLLAMA_IMAGE,
        GPU_TYPE,
        GPU_COUNT,
        CONTAINER_DISK_SIZE_GB,
        NETWORK_VOLUME_ID,
        OLLAMA_MODEL_TO_PULL
    )

    if pod:
        print(f"Successfully requested Pod '{pod_name}' (ID: {pod['id']}).")
        print("Waiting for Pod to become running. This may take a few minutes as the image downloads and model pre-pulls...")
        
        # Polling for pod status. In a real application, consider webhooks or more robust retry logic.
        max_attempts = 60 # Check for up to 5 minutes (60 * 5 seconds)
        for attempt in range(1, max_attempts + 1):
            time.sleep(5) # Wait 5 seconds between checks
            try:
                current_pod = runpod.get_pod(pod['id'])
                if current_pod and current_pod.get('desiredStatus') == 'RUNNING':
                    print(f"Pod '{pod_name}' is now RUNNING.")
                    print(f"Public IP: {current_pod.get('publicIp', 'N/A')}")
                    # Extract port information for accessing Ollama
                    ports_info = current_pod.get('ports', {})
                    # Handle ports_info as dict or str
                    if isinstance(ports_info, str):
                        try:
                            ports_info = json.loads(ports_info)
                        except Exception:
                            ports_info = {}
                    if isinstance(ports_info, dict):
                        ollama_port = ports_info.get('11434/http', {}).get('publicPort', 'N/A')
                        ollama_proxy_url = ports_info.get('11434/http', {}).get('publicUrl', 'N/A')
                    else:
                        ollama_port = 'N/A'
                        ollama_proxy_url = 'N/A'
                    print(f"Ollama accessible via Public Port: {ollama_port} or Proxy URL: {ollama_proxy_url}")
                    print(f"To interact with Ollama, you might use: curl {ollama_proxy_url}/api/generate -d '{{\"model\": \"{OLLAMA_MODEL_TO_PULL}\", \"prompt\": \"Why is the sky blue?\"}}'")
                    break
                print(f"Attempt {attempt}/{max_attempts}: Current status of Pod '{pod_name}': {current_pod.get('desiredStatus', 'UNKNOWN')}")
            except runpod.error.QueryError as e:
                print(f"Error checking pod status: {e}. Retrying...")
        else:
            print(f"Pod '{pod_name}' did not reach RUNNING status in the expected time.")
            print("Please check RunPod console for logs and detailed status.")
    else:
        print("Failed to initiate RunPod creation.")

if __name__ == "__main__":
    main()