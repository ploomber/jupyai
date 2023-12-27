from jupyai.autocomplete import autocomplete


def test_generate_code_in_empty_notebook():
    command = """
# code to generate a scatterplot with 100 random numbers
# the random numbers should be stored in a data variable
"""
    expected = """
import matplotlib.pyplot as plt
import numpy as np

# Generate 100 random numbers
data = np.random.rand(100)

# Create scatter plot
plt.scatter(range(100), data)
plt.show()
"""
    cell_to_autocomplete = {
        "source": command,
        "id": "1",
    }

    assert (
        autocomplete(
            cell_to_autocomplete,
            [
                cell_to_autocomplete,
            ],
        ).strip()
        == expected.strip()
    )


def test_generate_code_with_existing_cells():
    command = "# code to generate a scatterplot with 100 random numbers"
    cell_to_autocomplete = {
        "source": command,
        "id": "1",
    }
    expected = ""

    assert (
        autocomplete(
            cell_to_autocomplete,
            [
                {"source": "import numpy as np", "id": "0"},
                cell_to_autocomplete,
                {"source": "x = 1", "id": "2"},
            ],
        )
        == expected
    )
