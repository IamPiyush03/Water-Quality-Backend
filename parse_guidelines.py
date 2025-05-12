from utils.parser import WHOGuidelinesParser
import os

def main():
    # Initialize parser
    parser = WHOGuidelinesParser("data/Water Quality Guidelines.pdf")
    
    # Parse guidelines
    print("Parsing WHO guidelines...")
    guidelines = parser.parse_guidelines()
    
    # Save guidelines
    output_path = "data/who_guidelines.json"
    success = parser.save_guidelines(output_path)
    
    if success:
        print(f"Guidelines parsed and saved to: {output_path}")
        print("Guidelines structure:")
        for param, data in guidelines.items():
            print(f"\n{param}:")
            print(f"  Range: {data['range']}")
            if 'low' in data['measures']:
                print(f"  Low measures: {data['measures']['low']}")
            if 'high' in data['measures']:
                print(f"  High measures: {data['measures']['high']}")
    else:
        print("Failed to parse and save guidelines!")

if __name__ == "__main__":
    main() 