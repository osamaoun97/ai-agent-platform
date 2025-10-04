from django.shortcuts import render


def home(request):
    """
    Main view function that renders the application's home page.

    This view serves as the entry point for the chat application's frontend.
    It renders the index.html template which contains the single-page application.

    Args:
        request (HttpRequest): Django request object containing metadata about the request

    Returns:
        HttpResponse: Rendered index.html template
    """
    return render(request, "index.html")
