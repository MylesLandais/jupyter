"""
cleanup_runpod_instances.py

Script to list and terminate all active RunPod GPU pods for the current API key.
Use this to avoid unnecessary charges for idle or test deployments.
"""

import os
import runpod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
if not RUNPOD_API_KEY:
    raise ValueError("RUNPOD_API_KEY environment variable not set.")
runpod.api_key = RUNPOD_API_KEY

def list_active_pods():
    """
    List all active pods for the current account.
    Returns a list of pod dicts.
    """
    pods = runpod.get_pods()
    # Optionally filter for only running or non-terminated pods
    active_pods = [pod for pod in pods if pod.get("desiredStatus") not in ("TERMINATED", "DELETED")]
    return active_pods

def terminate_pod(pod_id):
    """
    Terminate a pod by its ID.
    """
    try:
        runpod.terminate_pod(pod_id)
        print(f"Terminated pod: {pod_id}")
    except Exception as e:
        print(f"Error terminating pod {pod_id}: {e}")

def cleanup_all_pods():
    """
    List and terminate all active pods.
    """
    pods = list_active_pods()
    if not pods:
        print("No active pods found.")
        return
    print(f"Found {len(pods)} active pod(s). Terminating...")
    for pod in pods:
        pod_id = pod.get("id")
        pod_name = pod.get("name", "Unnamed")
        print(f"Terminating pod {pod_name} (ID: {pod_id})...")
        terminate_pod(pod_id)
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_all_pods()