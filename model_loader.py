import csv
import os # Import the os module

# --- Corrected Path Handling ---
# Get the directory where THIS script (model_loader.py) is located.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the full, absolute path to the CSV file next to this script.
CSV_PATH = os.path.join(SCRIPT_DIR, "model_reference.csv")
# --- End Correction ---

def load_models_from_csv(csv_path=CSV_PATH):
    """
    Loads model reference data from the specified CSV file.

    Args:
        csv_path (str): The full path to the CSV file.
                        Defaults to the path constructed relative
                        to this script's location.

    Returns:
        list: A list of dictionaries, where each dictionary represents a model.
              Returns an empty list if the file cannot be loaded or parsed.
    """
    models = []
    # Add a check to see if the constructed path actually exists before trying to open
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found at the expected location: {csv_path}")
        return models # Return empty list

    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Check if required columns exist (optional but good practice)
            required_columns = ["Company", "Model", "Version", "API Types", "Max Tokens per Call", "Input Token Cost ($ per 1M)", "Output Token Cost ($ per 1M)"]
            if not all(col in reader.fieldnames for col in required_columns):
                print(f"[ERROR] CSV file at {csv_path} is missing required columns.")
                print(f"Required: {required_columns}")
                print(f"Found: {reader.fieldnames}")
                return models

            for row_num, row in enumerate(reader, start=2): # start=2 for header row + 1-based index
                try:
                    # Normalize and parse API Types
                    api_types_raw = row.get('API Types', '') # Use .get for safety
                    api_types = [api.strip() for api in api_types_raw.split(',') if api.strip()]

                    # Defensive parse for all numeric fields
                    def parse_int(val):
                        val = str(val).strip()
                        return int(val.replace(',', '')) if val else None
                    def parse_float(val):
                        val = str(val).strip()
                        return float(val) if val else None

                    max_tokens = parse_int(row.get('Max Tokens per Call', ''))
                    input_cost = parse_float(row.get('Input Token Cost ($ per 1M)', ''))
                    output_cost = parse_float(row.get('Output Token Cost ($ per 1M)', ''))
                    video_cost = parse_float(row.get('Video Cost ($ per minute)', ''))
                    audio_cost = parse_float(row.get('Audio Cost ($ per minute)', ''))
                    image_cost = parse_float(row.get('Image Cost ($ per image)', ''))
                    flat_file_cost = parse_float(row.get('Flat File Cost', ''))

                    models.append({
                        "company": row.get("Company", "N/A"),
                        "model": row.get("Model", "N/A"),
                        "version": row.get("Version", "N/A"),
                        "api_types": api_types,
                        "max_tokens": max_tokens,
                        "input_cost": input_cost,
                        "output_cost": output_cost,
                        "video_cost": video_cost,
                        "audio_cost": audio_cost,
                        "image_cost": image_cost,
                        "flat_file_cost": flat_file_cost,
                        "notes": row.get("Notes", "")
                    })
                except Exception as ve:
                    print(f"[ERROR] Skipping row {row_num} in {csv_path} due to data conversion error: {ve}")
                    print(f"Problematic row data: {row}")
                except KeyError as ke:
                    print(f"[ERROR] Skipping row {row_num} in {csv_path} due to missing column: {ke}")
                    print(f"Problematic row data: {row}")

    except FileNotFoundError:
        # This specific error should be less likely now with the os.path.exists check, but keep for safety
        print(f"[ERROR] Failed to load model data: File not found at {csv_path}")
    except Exception as e:
        # Catch other potential errors during file reading or CSV parsing
        print(f"[ERROR] Failed to load model data from {csv_path}: {e}")

    if not models:
        print(f"[WARNING] No models were successfully loaded from {csv_path}.")

    return models

# Example of how to test this module directly (optional)
if __name__ == "__main__":
    print(f"Attempting to load models directly from: {CSV_PATH}")
    loaded_models = load_models_from_csv()
    if loaded_models:
        print(f"Successfully loaded {len(loaded_models)} models.")
        # print("First model:", loaded_models[0])
    else:
        print("Failed to load models when running script directly.")
