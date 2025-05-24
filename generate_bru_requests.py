"""Generate Bruno request files from JSON input using specified templates and package them into a ZIP archive."""

import os
import json
import zipfile
from datetime import datetime

# === CONFIGURATION ===
ORDER_TEMPLATE_PATH = "Order Pre-Auth Risk Inquiry.bru.txt"
UPDATE_TEMPLATE_PATH = "Update Order -Last Created Order-.bru.txt"
INPUT_JSON_PATH = "combined_order_requests.json"
OUTPUT_DIR = "bruno_requests"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_ZIP_PATH = f"bruno_requests_{timestamp}.zip"


# === HELPER FUNCTION ===
def build_bru_file(template_str, name, seq, body_json):
    """
    Build a Bruno request file content from a template string by replacing placeholders.

    Parameters:
        template_str (str): The template content as a string.
        name (str): The name value to insert into the template.
        seq (int): The sequence number to insert into the template.
        body_json (dict): The JSON body to embed in the request.

    Returns:
        str: The complete Bruno request file content as a string.
    """
    lines = []
    for line in template_str.splitlines():
        if line.strip().startswith("name:"):
            lines.append(f"  name: {name}")
        elif line.strip().startswith("seq:"):
            lines.append(f"  seq: {seq}")
        else:
            lines.append(line)
    lines.append("")
    lines.append("body:json {")
    lines.extend(["  " + line for line in json.dumps(body_json, indent=2).splitlines()])
    lines.append("}")
    return "\n".join(lines)


# === LOAD TEMPLATES AND INPUT ===
with open(ORDER_TEMPLATE_PATH, "r", encoding="utf-8") as f:
    order_bru_template = f.read()

with open(UPDATE_TEMPLATE_PATH, "r", encoding="utf-8") as f:
    update_bru_template = f.read()

with open(INPUT_JSON_PATH, "r",  encoding="utf-8") as f:
    request_data = json.load(f)

# === GENERATE BRUNO REQUEST FILES ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

for idx, item in enumerate(request_data):
    payload = item["payload"]
    req_type = item["type"]
    seq = idx + 1
    name = f"{req_type} - {payload['merchantOrderId']}"
    filename = os.path.join(OUTPUT_DIR, f"{seq:03}_{req_type}.bru")

    template = order_bru_template if req_type == "OrderRequest" else update_bru_template
    bru_content = build_bru_file(template, name, seq, payload)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(bru_content)

# === ZIP THE RESULTS ===
with zipfile.ZipFile(OUTPUT_ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(OUTPUT_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, OUTPUT_DIR)
            zipf.write(full_path, arcname)

print(f"✔ Bruno requests generated and saved to {OUTPUT_ZIP_PATH}")
