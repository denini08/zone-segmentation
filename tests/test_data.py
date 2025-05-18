"""Test the python functions from src."""

import sys

import jax
import SimpleITK as sitk  # noqa: N813

jax.config.update("jax_platform_name", "cpu")
sys.path.insert(0, "./src/")

from src.medseg.data_loader import Loader
from src.medseg.util import compute_roi, resample_image


def test_data() -> None:
    """See if the function really returns true."""
    loader = Loader()
    
    # check if patient_keys is empty
    assert loader.patient_keys, "No patient data loaded: patient_keys is empty"
    
    test_anno_raw = []
    for key in loader.patient_keys:
        test_anno_raw.append(key in loader.patient_series_dict.keys())
    assert all(test_anno_raw), "Some patient keys are not in patient_series_dict"
    
    test_raw_complete = []
    interesting_scans = ["t2_tse_tra", "t2_tse_sag", "t2_tse_cor"]
    for key in loader.patient_keys:
        for scan in interesting_scans:
            entry = loader.patient_series_dict[key]
            test_raw_complete.append(scan in entry.keys())
    assert all(test_raw_complete), "Some required scans are missing for one or more patients"


def test_batch_assembly() -> None:
    """Ensure scans and annotations have the same size."""
    loader = Loader()
    record = loader.get_record("ProstateX-0311")
    assert record["images"].shape == record["annotation"].shape

    batch = loader.get_batch(8)
    assert batch["images"].shape == batch["annotation"].shape


def test_roi() -> None:
    """Ensure the region of interest computation works as intendet."""
    loader = Loader()
    t2w_img, sag_img, cor_img = loader.get_images("ProstateX-0311")
    t2w_img = resample_image(t2w_img, [0.5, 0.5, 3.0], sitk.sitkLinear, 0)
    sag_img = resample_image(sag_img, [0.5, 0.5, 3.0], sitk.sitkLinear, 0)
    cor_img = resample_image(cor_img, [0.5, 0.5, 3.0], sitk.sitkLinear, 0)

    _, slices = compute_roi((t2w_img, cor_img, sag_img))

    assert slices[0][0] == slice(102, 277, None)
