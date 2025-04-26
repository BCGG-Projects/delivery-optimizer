from data_generator import DataGenerator
from warehouses_logic import WarehousesLogic
from utils import to_json

if __name__ == "__main__":
    generator = DataGenerator()
    input_data = generator.generate()
    print(to_json(input_data))

    print(WarehousesLogic(input_data["warehouses"]).show_warehouses())
