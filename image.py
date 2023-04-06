from src import SphericalLens, Ray, ScenePlotter
import matplotlib.pyplot as plt


def main():
    n = 1.5
    R1 =  50
    R2 = -50
    thickness = 10
    paraxial_over_f = (n-1)*(1/R1-1/R2)
    f = 1/paraxial_over_f

    position = (0, 0, 100)

    obj = (0, 0, 0)

    lens = SphericalLens(n, R1, R2, position, thickness)

    plotter = ScenePlotter("object.svg", [0, 200, -30, 30], resolution=10)
    betas = [i/100 for i in range(-10, 10)]
    obj_position = (0, -10, 0)
    for beta in betas:
        gamma = (1-beta*beta)**.5
        ray = Ray(obj_position, (0, beta, gamma), 1.)
        lens.trace_ray(ray)

        ray.march_delta_z(f*2)

        plotter.draw_ray(ray)
    plotter.draw_object(lens)
    plotter.save_and_close()

if __name__ == "__main__":
    main()
