"""
inspect_running_pods.py

Script to inspect currently running RunPod instances to understand the correct
API parameters and configuration for successful pod creation.
"""

import os
import runpod
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
if not RUNPOD_API_KEY:
    raise ValueError("RUNPOD_API_KEY environment variable not set.")
runpod.api_key = RUNPOD_API_KEY

def inspect_active_pods():
    """
    Inspect all active pods to understand their configuration.
    """
    try:
        pods = runpod.get_pods()
        active_pods = [pod for pod in pods if pod.get("desiredStatus") not in ("TERMINATED", "DELETED")]
        
        if not active_pods:
            print("No active pods found.")
            return []
        
        print(f"Found {len(active_pods)} active pod(s):")
        print("=" * 80)
        
        for i, pod in enumerate(active_pods, 1):
            pod_id = pod.get("id", "N/A")
            pod_name = pod.get("name", "Unnamed")
            status = pod.get("desiredStatus", "UNKNOWN")
            
            # GPU information
            gpu_info = pod.get("gpu", {})
            gpu_type = gpu_info.get("displayName", "N/A")
            gpu_id = gpu_info.get("id", "N/A")
            
            # Pricing and instance type
            cost_per_hr = pod.get("costPerHr", "N/A")
            interruptible = pod.get("interruptible", False)
            
            # Runtime information
            runtime = pod.get("runtime", {})
            uptime = runtime.get("uptimeInSeconds", 0)
            
            print(f"\nPod {i}: {pod_name}")
            print(f"  ID: {pod_id}")
            print(f"  Status: {status}")
            print(f"  GPU Type: {gpu_type}")
            print(f"  GPU ID: {gpu_id}")
            print(f"  Cost per Hour: ${cost_per_hr}")
            print(f"  Interruptible (Spot): {interruptible}")
            print(f"  Uptime: {uptime} seconds")
            
            # Show key configuration fields
            print(f"  Image: {pod.get('image', 'N/A')}")
            print(f"  Ports: {pod.get('ports', 'N/A')}")
            print(f"  Volume GB: {pod.get('volumeInGb', 'N/A')}")
            print(f"  Container Disk GB: {pod.get('containerDiskInGb', 'N/A')}")
            
            # Environment variables
            env_vars = pod.get("env", {})
            if env_vars:
                print(f"  Environment Variables:")
                for key, value in env_vars.items():
                    print(f"    {key}: {value}")
            
            # Network volume
            network_volume = pod.get("networkVolume")
            if network_volume:
                print(f"  Network Volume: {network_volume.get('name', 'N/A')} ({network_volume.get('size', 'N/A')}GB)")
            
            print("-" * 40)
        
        # Look for RTX 5090 specifically
        rtx_5090_pods = [pod for pod in active_pods if "5090" in pod.get("gpu", {}).get("displayName", "")]
        if rtx_5090_pods:
            print(f"\nFound {len(rtx_5090_pods)} RTX 5090 pod(s):")
            for pod in rtx_5090_pods:
                print(f"\nRTX 5090 Pod Configuration:")
                print(f"  Name: {pod.get('name')}")
                print(f"  GPU ID: {pod.get('gpu', {}).get('id')}")
                print(f"  Interruptible: {pod.get('interruptible')}")
                print(f"  Cost: ${pod.get('costPerHr')}/hr")
                print(f"  Image: {pod.get('image')}")
                
                # Show the exact pod configuration for replication
                print(f"\nExact Configuration for Replication:")
                config_fields = [
                    'name', 'image', 'gpu', 'volumeInGb', 'containerDiskInGb', 
                    'ports', 'env', 'interruptible', 'networkVolume'
                ]
                
                for field in config_fields:
                    value = pod.get(field)
                    if value is not None:
                        if isinstance(value, dict):
                            print(f"  {field}: {json.dumps(value, indent=4)}")
                        else:
                            print(f"  {field}: {value}")
        
        return active_pods
        
    except Exception as e:
        print(f"Error inspecting pods: {e}")
        return []

def show_gpu_configuration(pod):
    """
    Show the exact GPU configuration from a running pod.
    """
    gpu_info = pod.get("gpu", {})
    print(f"\nGPU Configuration:")
    print(f"  ID: {gpu_info.get('id')}")
    print(f"  Display Name: {gpu_info.get('displayName')}")
    print(f"  Count: {gpu_info.get('count', 1)}")
    
    # Show pricing information if available
    price_fields = ['communityPrice', 'securePrice', 'communitySpotPrice', 'secureSpotPrice']
    for field in price_fields:
        if field in gpu_info:
            print(f"  {field}: ${gpu_info[field]}")

if __name__ == "__main__":
    active_pods = inspect_active_pods()
    
    if active_pods:
        print(f"\n" + "=" * 80)
        print("SUMMARY FOR NOTEBOOK CONFIGURATION")
        print("=" * 80)
        
        # Find the best example pod (preferably RTX 5090)
        rtx_5090_pods = [pod for pod in active_pods if "5090" in pod.get("gpu", {}).get("displayName", "")]
        
        if rtx_5090_pods:
            example_pod = rtx_5090_pods[0]
            print(f"Using RTX 5090 pod as example: {example_pod.get('name')}")
        else:
            example_pod = active_pods[0]
            print(f"Using first available pod as example: {example_pod.get('name')}")
        
        # Extract key configuration
        gpu_id = example_pod.get("gpu", {}).get("id", "NVIDIA GeForce RTX 5090")
        is_interruptible = example_pod.get("interruptible", False)
        cost_per_hr = example_pod.get("costPerHr", "N/A")
        image = example_pod.get("image", "ashleykleynhans/comfyui:latest")
        
        print(f"\nKey Configuration:")
        print(f"  GPU ID: {gpu_id}")
        print(f"  Interruptible: {is_interruptible}")
        print(f"  Cost: ${cost_per_hr}/hr")
        print(f"  Image: {image}")
        
        print(f"\nThis configuration should be used in the notebook for successful pod creation.")