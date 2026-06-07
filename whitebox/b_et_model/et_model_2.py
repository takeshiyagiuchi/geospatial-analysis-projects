import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt


def potential_et(ep: float, day_of_year: int | npt.NDArray) -> float | npt.NDArray:
    """
    Calculate daily potential evapotranspiration (ET).

    Parameters
    ----------
    ep : float
        Climatological mean daily potential ET (mm/day)
    day_of_year : int or array-like
        Day of year (1–366)

    Returns
    -------
    float
        Potential evapotranspiration (mm/day)
    """
    return ep * (1 + np.sin(np.deg2rad((360 * day_of_year / 365) - 90)))


def main():
    # EP input
    while True:
        try:
            ep_input = float(input("Enter climatological mean daily ET (mm/day): "))
            if ep_input <= 0:
                raise ValueError("ET must be a positive number.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    # Days of the year
    days = np.arange(1, 366)

    # Calculate ET
    et = potential_et(ep=ep_input, day_of_year=days)

    # Plot
    plt.figure()
    plt.plot(days, et)   # type: ignore[arg-type]
    plt.xlabel("Day of Year")
    plt.ylabel("Potential ET (mm/day)")
    plt.title("Simplistic Potential Evapotranspiration Model")
    plt.show()


if __name__ == "__main__":
    main()
