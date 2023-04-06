from src import SphericalLens, Ray, ScenePlotter
import matplotlib.pyplot as plt

def test():
    n = 1.5
    R1 =  50
    R2 = -50
    thickness = 10
    paraxial_over_f = (n-1)*(1/R1-1/R2)
    print(f"Focal lent prima = {1/paraxial_over_f} mm")

    position = (0, 0, 10)
    position2 = (0, 0, position[2]+2/paraxial_over_f)

    lens = SphericalLens(n, R1, R2, position, thickness)
    lens2 = SphericalLens(n, R1, R2, position2, thickness)
    heights = list(range(-int(lens.maximum_height*.9), int(lens.maximum_height*.9), 1))
    momenta = []
    par_momenta = []
    plotter = ScenePlotter("test.pdf", 1280, 480, [0, 100, -30, 30])
    for height in heights:
        ray = Ray((0, height, 0), (0, 0, 1), 1.)
        lens.trace_ray(ray)
        par_momenta.append(-ray.position[1]*paraxial_over_f)
        momenta.append(ray.momentum[1])

        lens2.trace_ray(ray, debug=False)
        #print(ray.trajectory[2][2], ray.trajectory[3][2])
        ray.march_delta_z(50)
        plotter.draw_ray(ray)

    plotter.draw_object(lens)
    plotter.draw_object(lens2)
    plotter.save_and_close()

    fig, ax = plt.subplots(1, 1, constrained_layout=True)
    ax.plot(heights, momenta, label="Ray traced momenta")
    ax.plot(heights, par_momenta, label="Paraxial momenta")
    ax.set_xlabel("Ray height (mm)")
    ax.set_ylabel("Ray momentum")

    ax.legend(loc="best")
    fig.savefig("momenta-f50.png", bbox_inches="tight", dpi=200)
    plt.show()

if __name__ == "__main__":
    test()
