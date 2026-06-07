from math import sin

def main():
    try:
        # Your ET model implementation goes here
        ep = float(input("Enter potential evapotranspiration (Ep) value: "))
        print(f"Calculating ET using Ep = {ep}")

        # ET = Ep [1 + sin(360i / 365 – 90)]
        for i in range(1, 366):
            et = ep * (1.0 + sin(360.0 * i / 365.0 - 90.0))
            print(f"{i},{et}")

        print("Done!")
    except Exception as e:
        print(f"An error occurred: {e}")

main()