import pandas as pd
import random
import string


class DummyOperations:
    def __init__(self, data_size=1000):
        self.data_size = data_size
        self.df = self._generate_dummy_data()

    def _random_name(self):
        # Generate a random name of the form 'NameX'
        return "Name" + "".join(random.choices(string.ascii_uppercase, k=3))

    def _random_email(self):
        # Generate a random email of the form 'userXYZ@example.com'
        user = "".join(random.choices(string.ascii_lowercase, k=7))
        return f"{user}@example.com"

    def _generate_dummy_data(self):
        """Create dummy dataset using Python's random module"""
        data = {
            "name": [self._random_name() for _ in range(self.data_size)],
            "email": [self._random_email() for _ in range(self.data_size)],
            "transaction": [
                random.randint(10000, 99999) for _ in range(self.data_size)
            ],
        }
        return pd.DataFrame(data)

    def process_data(self):
        """Simulate data processing workload"""
        # Create dummy variables from categorical data
        processed_df = pd.get_dummies(self.df["name"])
        # Numerical operations
        processed_df["scaled_transaction"] = self.df["transaction"] * 1.5
        return processed_df.sum().sum()
