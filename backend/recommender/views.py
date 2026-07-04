from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import search_anime, get_recommendations
from .serializers import AnimeSerializer


@api_view(["GET"])
def search(request):
    """
    GET /api/search/?q=naruto
    Returns up to 10 anime whose names contain the query string.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return Response(
            {"error": "Query parameter 'q' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    results = search_anime(query)
    serializer = AnimeSerializer(results, many=True)
    return Response({"results": serializer.data})


@api_view(["GET"])
def recommend(request):
    """
    GET /api/recommend/?name=Naruto
    Returns top 10 content-based recommendations for the given anime.
    """
    name = request.GET.get("name", "").strip()
    if not name:
        return Response(
            {"error": "Query parameter 'name' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    recommendations = get_recommendations(name)
    if not recommendations:
        return Response(
            {"error": f"Anime '{name}' not found in dataset."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AnimeSerializer(recommendations, many=True)
    return Response({"recommendations": serializer.data})