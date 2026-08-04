import matplotlib.pyplot as plt
import matplotlib.colors as mc
import numpy as np
import constants as c
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import math


def plot_radiation_patterns(results, file_title, beam_loc=None):
    f = plt.figure(dpi=150)
    factor = 180.0 / np.pi
    shifted_angles = ((results[0][0] + np.pi) % (2 * np.pi) - np.pi) * factor
    for result in results:
        if result[2] == "data":
            plt.plot(shifted_angles, result[1], "-", color="black")
    if beam_loc:
        for beam in beam_loc:
            plt.plot(beam[0] * factor, beam[1], "o", color="black")
    ax = plt.gca()
    ax.set_ylim(-31, 3)
    ax.set_xlim(-90, 90)
    ax.set_xticks([-90, -45, 0, 45, 90])
    ax.set_yticks([-c.beam_threshold, 0])
    ax.grid(True)
    ax.tick_params(labelsize=18)
    plt.savefig(file_title)
    plt.close()


def plot_radiation_patterns_polar(results, frequency) -> None:
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    # all_directivities = [result[1] for result in results]
    # global_max = np.max(all_directivities)
    # global_min = np.min(all_directivities)
    color_norm = mc.Normalize(vmin=c.sweep_start, vmax=c.sweep_stop)
    my_cmap = plt.colormaps["cool"]
    res_base_frequency = results[0]
    res = results[1]
    angles_res = res[0]
    directivity_res = res[1]
    angles_base_freq = res_base_frequency[0]
    directivity_base_freq = res_base_frequency[1]
    rgba_color = my_cmap(color_norm(frequency))
    ax.plot(angles_res, directivity_res, color=rgba_color)
    ax.plot(angles_base_freq, directivity_base_freq, color="b")
    ax.set_rlim(bottom=-31, top=3)
    sm = plt.cm.ScalarMappable(cmap=my_cmap, norm=color_norm)
    cbar = fig.colorbar(sm, ax=ax, pad=0.1)
    cbar.set_label("Frequency")
    # ax.set_rticks(-c.beam_threshold, 0)

    plt.savefig("rad_pattern_polar" + "_" + format(frequency, ".2f") + ".png")
    plt.close()


def plot_radiation_patterns_polar_plotly(all_results: list[dict]) -> None:
    df = pd.DataFrame(all_results)
    fig = go.Figure()
    groups = df.groupby("frequency")
    for freq, subset in groups:
        fig.add_trace(
            go.Scatterpolar(
                r=subset.directivity,
                theta=subset.angles * 180 / math.pi,
                mode="lines",
                name=f"{freq:.2f}",
                line_color="peru",
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(range=[min(df.directivity), max(df.directivity)]))
    )

    for i in range(1, len(fig.data)):
        fig.data[i].visible = False

    frames = []
    for i, freq in enumerate(sorted(groups.groups.keys())):
        frames.append(
            go.Frame(
                data=[
                    go.Scatterpolar(
                        r=fig.data[i].r,
                        theta=fig.data[i].theta,
                        mode="lines",
                        line_color="peru",
                    )
                ],
                name=f"{freq:.2f}",
            )
        )
    fig.frames = frames

    steps = []
    for freq in sorted(groups.groups.keys()):
        steps.append(
            dict(
                method="animate",
                label=f"{freq:.2f}",
                args=[
                    [f"{freq:.2f}"],
                    {
                        "mode": "immediate",
                        "frame": {"duration": 100, "redraw": True},
                        "transition": {"duration": 0},
                    },
                ],
            )
        )

    fig.update_layout(
        sliders=[
            dict(
                active=0,
                currentvalue={"prefix": "Frequency: "},
                pad={"t": 50},
                steps=steps,
            )
        ],
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 100, "redraw": True},
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                            },
                        ],
                    ),
                ],
            )
        ],
    )

    fig.write_html("my_plot.html", auto_open=True)


def plot_radiation_patterns_polar_plotly2(all_results: list[dict]) -> None:
    df = pd.DataFrame(all_results)
    fig = px.line_polar(
        data_frame=df,
        r="directivity",
        theta="angles",
        color="frequency",
        line_close=True,
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        template="plotly_dark",
        start_angle=0,
        # animation_frame="frequency",
        # animation_group="directivity",
    )
    # fig.show()
    fig.write_html("my_plot2.html", auto_open=True)
