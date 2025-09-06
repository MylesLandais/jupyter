#!/usr/bin/env python3
"""
RunPod GPU Availability Checker

This script checks current GPU availability on RunPod and provides
recommendations for when no GPUs are available.
"""

import os
import runpod
import time
from dotenv import load_dotenv
from datetime import datetime

def check_gpu_availability():
    """Check and display current GPU availability on RunPod."""
    
    # Load environment variables
    load_dotenv()
    
    RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
    if not RUNPOD_API_KEY:
        print("Error: RUNPOD_API_KEY environment variable not set.")
        print("Please set it in your .env file.")
        return False
    
    runpod.api_key = RUNPOD_API_KEY
    print(f"RunPod API key loaded: {RUNPOD_API_KEY[:16]}...")
    print(f"Checking availability at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        gpus = runpod.get_gpus()
        
        available_gpus = []
        all_gpus = []
        
        for gpu in gpus:
            gpu_id = gpu.get('id', 'N/A')
            gpu_name = gpu.get('displayName', 'N/A')
            memory_gb = gpu.get('memoryInGb', 'N/A')
            
            # Get pricing info
            lowest_price = gpu.get('lowestPrice', {})
            price_per_hour = lowest_price.get('minimumBidPrice', 'N/A')
            available_count = lowest_price.get('uninterruptableCountAvailable', 0)
            spot_count = lowest_price.get('interruptableCountAvailable', 0)
            
            gpu_info = {
                'id': gpu_id,
                'name': gpu_name,
                'memory': memory_gb,
                'price': price_per_hour,
                'available': available_count,
                'spot_available': spot_count
            }
            
            all_gpus.append(gpu_info)
            
            if available_count > 0 or spot_count > 0:
                available_gpus.append(gpu_info)
        
        # Display results
        if available_gpus:
            print("AVAILABLE GPUs:")
            print("-" * 80)
            for gpu in available_gpus:
                on_demand = f"On-demand: {gpu['available']}" if gpu['available'] > 0 else "On-demand: 0"
                spot = f"Spot: {gpu['spot_available']}" if gpu['spot_available'] > 0 else "Spot: 0"
                print(f"ID: {gpu['id']}")
                print(f"   Name: {gpu['name']} ({gpu['memory']}GB)")
                print(f"   Price: ${gpu['price']}/hr")
                print(f"   Available: {on_demand} | {spot}")
                print()
        else:
            print("NO GPUs CURRENTLY AVAILABLE")
            print("-" * 80)
            print("\nAll GPU types (for reference):")
            print("-" * 40)
            
            # Sort by memory for better display
            sorted_gpus = sorted(all_gpus, key=lambda x: x['memory'] if isinstance(x['memory'], (int, float)) else 0, reverse=True)
            
            for gpu in sorted_gpus[:15]:  # Show top 15
                print(f"{gpu['name']} ({gpu['memory']}GB) - ${gpu['price']}/hr - ID: {gpu['id']}")
            
            print("\n" + "=" * 80)
            print("RECOMMENDATIONS WHEN NO GPUs ARE AVAILABLE:")
            print("=" * 80)
            print("1. TIMING: Try again in 5-15 minutes - availability changes frequently")
            print("2. SPOT INSTANCES: Consider interruptible instances if available")
            print("3. ALTERNATIVES: Check other cloud providers (Vast.ai, Lambda Labs)")
            print("4. NOTIFICATIONS: Set up RunPod notifications for preferred GPU types")
            print("5. FLEXIBLE TIMING: Off-peak hours (late night/early morning) often have better availability")
            print("6. LOWER-END GPUs: Consider RTX 4090 or RTX 3090 if RTX 5090 unavailable")
            
            print("\nCOMFYUI MINIMUM REQUIREMENTS:")
            print("- 8GB+ VRAM recommended (RTX 3080 or better)")
            print("- 16GB+ VRAM for complex workflows (RTX 4090/5090)")
            print("- 24GB+ VRAM for large models (RTX 4090/5090/A6000)")
        
        return len(available_gpus) > 0
        
    except Exception as e:
        print(f"Error checking GPU availability: {e}")
        return False

def monitor_availability(check_interval_minutes=5, max_checks=12):
    """Monitor GPU availability over time."""
    
    print(f"Monitoring GPU availability every {check_interval_minutes} minutes...")
    print(f"Will check {max_checks} times (total: {max_checks * check_interval_minutes} minutes)")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 80)
    
    for i in range(max_checks):
        print(f"\nCheck {i+1}/{max_checks}:")
        
        if check_gpu_availability():
            print("\nGPUs found! You can now create your ComfyUI pod.")
            return True
        
        if i < max_checks - 1:  # Don't sleep after last check
            print(f"\nWaiting {check_interval_minutes} minutes before next check...")
            try:
                time.sleep(check_interval_minutes * 60)
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user.")
                return False
    
    print(f"\nCompleted {max_checks} checks. No GPUs became available.")
    print("Try running the script again later or check RunPod console directly.")
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_availability()
    else:
        check_gpu_availability()
        print("\nTo monitor availability over time, run:")
        print("python check_runpod_availability.py monitor")