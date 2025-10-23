#!/usr/bin/env python3
"""Debug script to check configuration and MCP server."""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("=" * 60)
    print("Checking Environment Configuration")
    print("=" * 60)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Please create .env file with required variables.")
        print("   You can copy from .env.example if available.")
        return False
    
    print("✓ .env file exists")
    
    # Try to load and check variables
    try:
        from config import settings
        
        print("\nChecking required environment variables:")
        
        # Check OpenAI API Key
        if settings.openai_api_key:
            print(f"✓ OPENAI_API_KEY: {'*' * 20}{settings.openai_api_key[-4:]}")
        else:
            print("❌ OPENAI_API_KEY: Not set")
        
        # Check Harness Account ID
        if settings.harness_account_id:
            print(f"✓ HARNESS_ACCOUNT_ID: {settings.harness_account_id}")
        else:
            print("❌ HARNESS_ACCOUNT_ID: Not set")
        
        # Check Harness API Key
        if settings.harness_api_key:
            print(f"✓ HARNESS_API_KEY: {'*' * 20}{settings.harness_api_key[-4:]}")
        else:
            print("❌ HARNESS_API_KEY: Not set")
        
        # Check Harness API URL
        print(f"✓ HARNESS_API_URL: {settings.harness_api_url}")
        
        # Check Harness Default Org ID
        if settings.harness_default_org_id:
            print(f"✓ HARNESS_DEFAULT_ORG_ID: {settings.harness_default_org_id}")
        else:
            print("❌ HARNESS_DEFAULT_ORG_ID: Not set")
        
        # Check Harness Default Project ID
        if settings.harness_default_project_id:
            print(f"✓ HARNESS_DEFAULT_PROJECT_ID: {settings.harness_default_project_id}")
        else:
            print("❌ HARNESS_DEFAULT_PROJECT_ID: Not set")
        
        # Check MCP Server Path
        if settings.mcp_server_path:
            print(f"✓ MCP_SERVER_PATH: {settings.mcp_server_path}")
            
            # Check if file exists and is executable
            mcp_path = Path(settings.mcp_server_path)
            if not mcp_path.exists():
                print(f"  ❌ File does not exist: {settings.mcp_server_path}")
                return False
            
            if not os.access(settings.mcp_server_path, os.X_OK):
                print(f"  ⚠️  File is not executable. Run: chmod +x {settings.mcp_server_path}")
                return False
            
            print(f"  ✓ File exists and is executable")
        else:
            print("❌ MCP_SERVER_PATH: Not set")
            return False
        
        print(f"\n✓ API will run on: {settings.api_host}:{settings.api_port}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading configuration: {e}")
        return False

def test_mcp_server():
    """Test if MCP server can be started."""
    print("\n" + "=" * 60)
    print("Testing MCP Server")
    print("=" * 60)
    
    try:
        from config import settings
        import subprocess
        
        if not settings.mcp_server_path:
            print("❌ MCP_SERVER_PATH not configured")
            return False
        
        print(f"Attempting to run: {settings.mcp_server_path}")
        print("This will test if the MCP server binary works...")
        print("(This may hang if the server is waiting for input - that's OK)")
        print("\nPress Ctrl+C to stop if it hangs...\n")
        
        # Try to run the MCP server with a timeout
        result = subprocess.run(
            [settings.mcp_server_path, "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 or "harness" in result.stdout.lower() or "mcp" in result.stdout.lower():
            print("✓ MCP server binary appears to be working")
            if result.stdout:
                print(f"\nOutput:\n{result.stdout[:500]}")
            return True
        else:
            print(f"⚠️  MCP server returned code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  MCP server command timed out (this might be normal)")
        print("   The server may be waiting for stdio input.")
        return True
    except FileNotFoundError:
        print(f"❌ MCP server binary not found: {settings.mcp_server_path}")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def main():
    """Main debug function."""
    print("\n🔍 Harness Agent Configuration Debugger\n")
    
    config_ok = check_env_file()
    
    if config_ok:
        print("\n✓ Configuration looks good!")
        
        # Ask if user wants to test MCP server
        try:
            response = input("\nTest MCP server binary? (y/n): ").strip().lower()
            if response == 'y':
                test_mcp_server()
        except KeyboardInterrupt:
            print("\n\nSkipping MCP server test.")
    else:
        print("\n❌ Configuration has issues. Please fix them before running the agent.")
        print("\nRequired steps:")
        print("1. Create .env file (copy from .env.example if available)")
        print("2. Set all required environment variables")
        print("3. Ensure MCP server binary exists and is executable")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Debug complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

