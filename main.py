from data_generator import DataGenerator
from utils import to_json

if __name__ == "__main__":
    generator = DataGenerator()
    input_data = generator.generate()
    print(to_json(input_data))
