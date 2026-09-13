from models import GDSIIFileConfigHorn

GDSII_CONFIG_TEST_HORN_1 = GDSIIFileConfigHorn(
    file_path="test_w_wire",
    horn_sides_layer=2,
    source_layer=7,
    horn_top_layer=10,
    back_plug_layer=8,
    main_conductive_layer=5,
    top_bottom_conductive_layer=1,
    main_dielectric_layer=6,
    top_bottom_dielectric_layer=4,
    wire_layer=3,
)