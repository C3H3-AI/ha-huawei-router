import os
import json
import urllib.request
import urllib.error

HA_URL = os.environ.get("HOMEASSISTANT_URL", "http://api.homediy.top:8123")
HA_TOKEN = os.environ.get("HOMEASSISTANT_TOKEN", "")

def call_service(domain, service, data=None):
    """Call a Home Assistant service."""
    url = f"{HA_URL}/api/services/{domain}/{service}"
    data = data or {}

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        try:
            error_body = json.loads(e.read())
            print(f"Error body: {error_body}")
        except:
            pass
        return None

def check_services():
    """Check available services."""
    url = f"{HA_URL}/api/services"

    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {HA_TOKEN}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            services = json.loads(response.read())
            return services
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("Home Assistant Service Checker")
    print("=" * 50)
    print(f"HA URL: {HA_URL}")
    print()

    if not HA_TOKEN:
        print("ERROR: HOMEASSISTANT_TOKEN not set")
        return

    # Check services
    print("Checking available services...")
    services = check_services()

    if services:
        print(f"Found {len(services)} domains with services:")
        for domain in sorted(services.keys()):
            domain_services = services[domain]
            print(f"  - {domain}: {len(domain_services)} services")
    else:
        print("Could not retrieve services")

    print()

    # Check if there's a shell_command service
    print("Checking for useful services...")

    useful_services = [
        ("shell_command", "reload"),
        ("hacs", "reload"),
        ("homeassistant", "reload_config_entry"),
    ]

    for domain, service in useful_services:
        result = call_service(domain, service)
        if result is not None:
            print(f"  ✓ {domain}.{service} - Available")
        else:
            print(f"  ✗ {domain}.{service} - Not available")

if __name__ == "__main__":
    main()
