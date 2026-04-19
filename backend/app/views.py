import json
from dataclasses import asdict

from django.conf import settings
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .domain.data_loader import DataLoader
from .domain.dataset_registry import DatasetRegistry
from .domain.provenance import build_provenance

from analysis_core.skymap.service import run_skymap


class InvalidRequestBodyError(Exception):
    """Raised when request body cannot be decoded/parsing as JSON."""


def _registry() -> DatasetRegistry:
    return DatasetRegistry(settings.TWAPP_DATASETS_FILE)


def _loader() -> DataLoader:
    return DataLoader(data_root=settings.TWAPP_DATA_DIR, registry=_registry())


def _validate_dataset(dataset_id: str) -> JsonResponse | None:
    try:
        ok, message = _loader().validate_dataset(dataset_id)
    except KeyError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    if not ok:
        return JsonResponse({"detail": message}, status=400)

    return None


@require_GET
def health(_: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok", "service": "telescope-webapp-api"})


@require_GET
def datasets(_: HttpRequest) -> JsonResponse:
    payload = [dataset.model_dump(mode="json") for dataset in _registry().list_datasets()]
    return JsonResponse(payload, safe=False)


@require_GET
def observations(_: HttpRequest, dataset_id: str) -> JsonResponse:
    try:
        ok, message = _loader().validate_dataset(dataset_id)
    except KeyError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    if not ok:
        return JsonResponse({"detail": message}, status=400)

    payload = [obs.model_dump(mode="json") for obs in _loader().list_observations(dataset_id)]
    return JsonResponse(payload, safe=False)


def _decode_body(request: HttpRequest) -> dict:
    if not request.body:
        return {}
    try:
        decoded_body = request.body.decode("utf-8")
        return json.loads(decoded_body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidRequestBodyError("Malformed JSON body") from exc

def _bad_request(message: str) -> JsonResponse:
    return JsonResponse({"detail": message}, status=400)

@require_POST
def theta2(request: HttpRequest) -> JsonResponse:
    try:
        payload = _decode_body(request)
    except InvalidRequestBodyError as exc:
        return HttpResponseBadRequest(str(exc))
    dataset_id = payload.get("dataset_id")
    if not dataset_id:
        return HttpResponseBadRequest("dataset_id is required")
    validation_error = _validate_dataset(dataset_id)
    if validation_error:
        return validation_error
    return JsonResponse(
        {
            "dataset_id": dataset_id,
            "message": "Theta² endpoint stub ready for analysis_core.theta2 integration",
            "provenance": asdict(build_provenance(dataset_id, "theta2")),
        }
    )


@require_POST
def skymap(request: HttpRequest) -> JsonResponse:
    try:
        payload = _decode_body(request)
    except InvalidRequestBodyError as exc:
        return _bad_request(str(exc))

    dataset_id = payload.get("dataset_id") or None
    if not dataset_id:
        return _bad_request("dataset_id is required")

    validation_error = _validate_dataset(dataset_id)
    if validation_error:
        return validation_error

    try:
        dataset = _registry().get_dataset(dataset_id)
        datastore_path = str(settings.TWAPP_DATA_DIR / dataset.datastore_path)
    except (KeyError, AttributeError) as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    _SKYMAP_PARAMS = (
        "width_deg",
        "binsz_deg",
        "energy_min_tev",
        "energy_max_tev",
        "ring_r_in_deg",
        "ring_width_deg",
        "exclusion_radius_deg",
        "correlation_radius_deg",
        "offset_max_deg",
    )
    kwargs = {key: payload[key] for key in _SKYMAP_PARAMS if key in payload}

    try:
        result = run_skymap(datastore_path=datastore_path, dataset_id=dataset_id, **kwargs)
    except Exception as exc:
        import traceback
        return JsonResponse({"detail": str(exc), "traceback": traceback.format_exc()}, status=500)

    return JsonResponse(
        {
            "dataset_id": dataset_id,
            "message": "Sky map generated",
            "data": result,
            "provenance": asdict(build_provenance(dataset_id, "skymap")),
        }
    )

@require_POST
def spectrum(request: HttpRequest) -> JsonResponse:
    try:
        payload = _decode_body(request)
    except InvalidRequestBodyError as exc:
        return HttpResponseBadRequest(str(exc))
    dataset_id = payload.get("dataset_id")
    if not dataset_id:
        return HttpResponseBadRequest("dataset_id is required")
    validation_error = _validate_dataset(dataset_id)
    if validation_error:
        return validation_error
    return JsonResponse(
        {
            "dataset_id": dataset_id,
            "message": "Spectrum endpoint stub ready for analysis_core.spectrum integration",
            "provenance": asdict(build_provenance(dataset_id, "spectrum")),
        }
    )


@require_POST
def lightcurve(request: HttpRequest) -> JsonResponse:
    try:
        payload = _decode_body(request)
    except InvalidRequestBodyError as exc:
        return HttpResponseBadRequest(str(exc))
    dataset_id = payload.get("dataset_id")
    if not dataset_id:
        return HttpResponseBadRequest("dataset_id is required")
    validation_error = _validate_dataset(dataset_id)
    if validation_error:
        return validation_error
    return JsonResponse(
        {
            "dataset_id": dataset_id,
            "message": "Light curve endpoint stub ready for analysis_core.lightcurve integration",
            "provenance": asdict(build_provenance(dataset_id, "lightcurve")),
        }
    )
