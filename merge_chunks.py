import os
import json
import math

# How many chunks to merge together
n = 5

input_folder = "jsons"
output_folder = "newjsons"

# Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# Loop through all JSON files
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        try:
            print(f"\nProcessing file: {filename}")

            file_path = os.path.join(input_folder, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            chunks = data.get("chunks", [])
            total_chunks = len(chunks)

            if total_chunks == 0:
                print("No chunks found. Skipping...")
                continue

            new_chunks = []
            num_groups = math.ceil(total_chunks / n)

            print(f"Total chunks: {total_chunks}")
            print(f"Merging into groups of {n}")
            print(f"Total merged groups: {num_groups}")

            for i in range(num_groups):
                start_idx = i * n
                end_idx = min((i + 1) * n, total_chunks)

                chunk_group = chunks[start_idx:end_idx]

                merged_chunk = {
                    "number": i + 1,
                    "title": chunk_group[0].get("title", ""),
                    "start": chunk_group[0].get("start", ""),
                    "end": chunk_group[-1].get("end", ""),
                    "text": " ".join(c.get("text", "") for c in chunk_group)
                }

                new_chunks.append(merged_chunk)

            # Save processed file
            output_path = os.path.join(output_folder, filename)

            with open(output_path, "w", encoding="utf-8") as json_file:
                json.dump({
                    "chunks": new_chunks,
                    "text": data.get("text", "")
                }, json_file, indent=4)

            print(f"Saved merged file to: {output_path}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("\n✅ All files processed successfully!")

    