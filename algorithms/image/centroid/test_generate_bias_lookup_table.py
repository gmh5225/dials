import pytest

from dials.algorithms.image.centroid.generate_bias_lookup_table import (
    compute_lookup_table,
)


def test_compute_lookup_table():
    sigma, bias_sq = compute_lookup_table()
    assert sigma == pytest.approx([0.01 * i for i in range(50)])
    assert bias_sq == pytest.approx(
        [
            0.08333333333333333,
            0.07779143749785543,
            0.07244954166237781,
            0.06730764582689962,
            0.06236574999142284,
            0.057623854155945314,
            0.053081958320467526,
            0.04874006248499069,
            0.044598166649512376,
            0.04065627081403469,
            0.036914374978527786,
            0.03337247914009149,
            0.030030583203638925,
            0.02688868576950588,
            0.023946775530827736,
            0.02120479466734718,
            0.018662535311000192,
            0.01631942920236463,
            0.014174222887642854,
            0.012224582589533621,
            0.010466711795097026,
            0.00889506912359066,
            0.007502246763131897,
            0.006279028368636448,
            0.005214607683692392,
            0.0042969251778479135,
            0.0035130711928804048,
            0.002849706975435916,
            0.0022934645546688233,
            0.0018312983836337626,
            0.0014507731386808529,
            0.001140281595737725,
            0.0008891936091121919,
            0.0006879420155134413,
            0.0005280541386423972,
            0.0004021389092032845,
            0.00030383984536079436,
            0.00022776360214798853,
            0.00016939277198554838,
            0.00012499031969171728,
            9.150163037978207e-05,
            6.645876013724184e-05,
            4.789019281294818e-05,
            3.423827569868347e-05,
            2.4285560546372603e-05,
            1.7090521999925317e-05,
            1.1932555733607008e-05,
            8.265755667370042e-06,
            5.680709799681428e-06,
            3.8734110957129664e-06,
        ]
    )
