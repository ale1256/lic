import os

def create_key(template, outtype=("nii.gz",), annotation_classes=None):
    if template is None or not template:
        raise ValueError("Template must be a valid format string")
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    t1w = create_key("sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w")
    func = create_key(
        "sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_bold"
    )

    info = {t1w: [], func: []}
    session = "ses-BL"

    for s in seqinfo:
        p_name = str(s.protocol_name).upper()
        s_desc = str(s.series_description).upper()
        header_info = p_name + " " + s_desc
        if ("MPRAGE" in header_info) or ("T1" in p_name):
            if s.dim3 > 50:
                info[t1w].append(s.series_id)
        if (
            ("RESTING" in header_info)
            or ("BOLD" in header_info)
            or ("EP2D" in header_info)
        ):
            info[func].append(s.series_id)

    return info
