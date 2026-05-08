import httpx
from fastapi import HTTPException, status

ART_INSTITUTE_BASE_URL= "https://api.artic.edu/api/v1/artworks"

async def verify_place_exists(external_id: int) -> bool:
    """
    Makes a request to the Art Institute API to check for the existence of an object.
    Returns True if the object is found, False if 404.
    Throws an HTTPException (503) when the API fails.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Form the URL: https://api.artic.edu/api/v1/artworks/{external_id} and require the API to return only the id
            response = await client.get(
                f"{ART_INSTITUTE_BASE_URL}/{external_id}",
                params={"fields": "id"},
                timeout=5
            )

            #if API return 200 - Good
            if response.status_code == 200:
                return True

            #if Api return 404 - place dont exist
            if response.status_code == 404:
                return False

            #if any other error occurred
            response.raise_for_status()

        except httpx.REquestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Art Institute API. Please try again later. Details: {str(exc)}"
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Art Institute API return error: {exc.response.status_code}"
            )