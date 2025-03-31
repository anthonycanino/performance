import sys
import argparse
from dataclasses import dataclass
from typing import List

# Record for Sample Histogram
@dataclass
class SampleHistogramRecord:
    from_value: int
    to_value: int
    count: int

# Record for Block Maps
@dataclass
class BlockMapRecord:
    native_offset: int
    il_offset: int
    samples: int

# Record for LBR Method
@dataclass
class LbrMethodRecord:
    method_name: str
    sample_histogram_data: List[SampleHistogramRecord]
    block_maps_data: List[BlockMapRecord]

class LBRParser:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self, method_name: str) -> List[LbrMethodRecord]:
        method_records: List[LbrMethodRecord] = []
        sample_histogram_data: List[SampleHistogramRecord] = []
        block_maps_data: List[BlockMapRecord] = []
        current_method_name = None

        with open(self.filepath, 'r') as file:
            lines = file.readlines()

        inside_sample_histogram = False
        inside_block_maps = False

        for line in lines:
            line = line.strip()

            # Detect the start of a new method block
            if line.startswith("@@@"):
                if current_method_name:
                    # Save the previous method record
                    method_records.append(LbrMethodRecord(
                        method_name=current_method_name,
                        sample_histogram_data=sample_histogram_data,
                        block_maps_data=block_maps_data
                    ))
                # Reset state for the next method
                current_method_name = None
                sample_histogram_data = []
                block_maps_data = []
                inside_sample_histogram = False
                inside_block_maps = False
                continue

            # Parse the method name
            if line.startswith("MethodName:"):
                parsed_method_name = line.split(":", 1)[1].strip()
                current_method_name = parsed_method_name if parsed_method_name == method_name else None

            # Capture data after ** Sample Histogram **
            if current_method_name and line.startswith("** Sample Histogram **"):
                inside_sample_histogram = True
                inside_block_maps = False
                continue

            if current_method_name and inside_sample_histogram:
                if line.startswith("** Block Maps **"):
                    inside_sample_histogram = False
                    inside_block_maps = True
                    continue
                if line:  # Skip empty lines
                    sample_histogram_data.append(self._parse_sample_histogram_line(line))

            # Capture data after ** Block Maps **
            if current_method_name and inside_block_maps:
                if line.startswith("@@@"):
                    inside_block_maps = False
                    continue
                if line:  # Skip empty lines
                    block_maps_data.append(self._parse_block_maps_line(line))

        # Append the last method record if still inside a matching method
        if current_method_name:
            method_records.append(LbrMethodRecord(
                method_name=current_method_name,
                sample_histogram_data=sample_histogram_data,
                block_maps_data=block_maps_data
            ))

        return method_records

    def _parse_sample_histogram_line(self, line: str) -> SampleHistogramRecord:
        """Parses a single line from the ** Sample Histogram ** section."""
        parts = line.split()
        from_value = int(parts[0].split(":")[1])
        to_value = int(parts[1].split(":")[1])
        count = int(parts[2].split(":")[1])
        return SampleHistogramRecord(from_value, to_value, count)

    def _parse_block_maps_line(self, line: str) -> BlockMapRecord:
        """Parses a single line from the ** Block Maps ** section."""
        parts = line.split()
        native_offset = int(parts[0].split(":")[1])
        il_offset = int(parts[1].split(":")[1])
        samples = int(parts[2].split(":")[1])
        return BlockMapRecord(native_offset, il_offset, samples)

# Record for Schema
@dataclass
class SchemaRecord:
    il_offset: int
    other: int
    schema_count: int

# Record for PGO Method
@dataclass
class PgoMethodRecord:
    method_name: str
    schema_records: List[SchemaRecord]

# Constants for Schema parsing
IL_OFFSET_INDEX = 4  # Index of the ILOffset value in the schema line
OTHER_INDEX = 8      # Index of the Other value in the schema line

class PGOParser:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self, method_name: str) -> List[PgoMethodRecord]:
        method_records: List[PgoMethodRecord] = []
        schema_records: List[SchemaRecord] = []
        current_method_name = None

        with open(self.filepath, 'r') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            line = line.strip()

            # Detect the start of a new method block
            if line.startswith("@@@"):
                if current_method_name:
                    # Save the previous method record
                    method_records.append(PgoMethodRecord(
                        method_name=current_method_name,
                        schema_records=schema_records
                    ))
                # Reset state for the next method
                current_method_name = None
                schema_records = []
                continue

            # Parse the method name
            if line.startswith("MethodName:"):
                parsed_method_name = line.split(":", 1)[1].strip()
                current_method_name = parsed_method_name if parsed_method_name == method_name else None

            # Parse Schema InstrumentationKind lines
            if current_method_name and line.startswith("Schema InstrumentationKind"):
                schema_record = self._parse_schema_line(line, lines[i + 1].strip())
                schema_records.append(schema_record)

        # Append the last method record if still inside a matching method
        if current_method_name:
            method_records.append(PgoMethodRecord(
                method_name=current_method_name,
                schema_records=schema_records
            ))

        return method_records

    def _parse_schema_line(self, schema_line: str, count_line: str) -> SchemaRecord:
        """Parses a Schema line and its following count line from the pgo-schema.txt file."""
        parts = schema_line.split()
        il_offset = int(parts[IL_OFFSET_INDEX])  # Value after "ILOffset"
        other = int(parts[OTHER_INDEX])         # Value after "Other"
        schema_count = int(count_line)          # Count value from the next line
        return SchemaRecord(il_offset, other, schema_count)

def main():
    parser = argparse.ArgumentParser(description="Analyze LBR and PGO files for a specific method.")
    parser.add_argument("lbr_file", help="Path to the LBR file.")
    parser.add_argument("pgo_file", help="Path to the PGO file.")
    parser.add_argument("method_name", help="The method name to analyze.")

    args = parser.parse_args()

    # Parse the LBR file
    lbr_parser = LBRParser(args.lbr_file)
    lbr_method_records = lbr_parser.parse(args.method_name)

    print(f"Method Name (LBR): {args.method_name}")
    for record in lbr_method_records:
        print("\nSample Histogram Data:")
        for hist_record in record.sample_histogram_data:
            print(hist_record)

        print("\nBlock Maps Data:")
        for block_record in record.block_maps_data:
            print(block_record)

    # Parse the PGO file
    pgo_parser = PGOParser(args.pgo_file)
    pgo_method_records = pgo_parser.parse(args.method_name)

    print(f"\nMethod Name (PGO): {args.method_name}")
    for record in pgo_method_records:
        print("\nSchema Records:")
        for schema_record in record.schema_records:
            print(schema_record)

if __name__ == "__main__":
    main()