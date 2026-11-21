from models import GDSIIFileConfigHorn

GDSII_CONFIG_TEST_HORN_TEST = GDSIIFileConfigHorn(
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
GDSII_CONFIG_TEST_HORN_RAD_PATTERN = GDSIIFileConfigHorn(
    file_path="horn_w_wire",
    top_bottom_conductive_layer=1,
    horn_sides_layer=2,
    wire_layer=3,
    top_bottom_dielectric_layer=4,
    main_conductive_layer=5,
    main_dielectric_layer=6,
    back_plug_layer=8,
    source_layer=7,  # this is the difference between them
    horn_top_layer=10,
)
GDSII_CONFIG_TEST_HORN_VSWR = GDSIIFileConfigHorn(
    file_path="horn_w_wire",
    top_bottom_conductive_layer=1,
    horn_sides_layer=2,
    wire_layer=3,
    top_bottom_dielectric_layer=4,
    main_conductive_layer=5,
    main_dielectric_layer=6,
    back_plug_layer=8,
    source_layer=9,  # this is the difference between them
    horn_top_layer=10,
)
