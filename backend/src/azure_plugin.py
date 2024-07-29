from typing import Annotated
from semantic_kernel import SKContext
from semantic_kernel.functions import kernel_function

class AzurePlugin:

    @kernel_function(
        name="search",
        description="Search azure for specific resources",
    )
    @kernel_function_context_parameter(name="resource", description="resource to search for")
    def search(
        self,
        context: SKContext
    ) -> Annotated[str, "the output is a string"]:
        """Gets a list of related azure resources"""
        return f"The results from your search are: {context['resource']}"