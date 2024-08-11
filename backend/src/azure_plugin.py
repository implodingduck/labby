from typing import Annotated
import semantic_kernel as sk
from semantic_kernel.functions import kernel_function

class AzurePlugin:

    @kernel_function(
        name="search",
        description="Search azure for specific resources",
    )
    def search(
        self,
    ) -> Annotated[str, "the output is a string"]:
        """Gets a list of related azure resources"""
        return f"The results from your search are: TBD"