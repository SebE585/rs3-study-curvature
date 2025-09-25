def theme():
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 150,
            "axes.grid": True,
            "grid.alpha": 0.2,
        }
    )
