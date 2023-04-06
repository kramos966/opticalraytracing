import cairo
import numpy as np

class ScenePlotter(object):
    def __init__(self, fname: str, extent: list, resolution=10):
        self.extent = extent
        # Position of the optical axis with respect to the surface
        x0, x1, y0, y1 = extent
        delta_x = x1-x0
        delta_y = y1-y0
        width = delta_x * resolution
        height = delta_y * resolution

        if fname.endswith(".svg"):
            self.surface = cairo.SVGSurface(fname, width, height)
        elif fname.endswith(".pdf"):
            self.surface = cairo.PDFSurface(fname, width, height)
        else:
            raise NameError("File extension is mandatory or not identified.")
        self.ctx = cairo.Context(self.surface)


        self.scale = min(width, height)/min(delta_x, delta_y)

        ##self.scale = self.pixel_length/
        self.transform = lambda x, y: (self.scale * (x-x0), self.scale * (y-y0))

    def draw_ray(self, ray):
        points = ray.trajectory
        surface_points = [self.transform(point[2], point[1]) for point in points]
        self.ctx.move_to(*surface_points[0])

        self.ctx.set_source_rgb(0, 1, .25)
        self.ctx.set_line_width(0.4)
        for point in surface_points[1:]:
            self.ctx.line_to(*point)
        # Pinta el traç finalment
        self.ctx.stroke()

    def draw_object(self, optical_element):
        # TODO: Tingues en compte també els casos que no siguin lents...
        spheres = optical_element.Spheres
        self.ctx.set_source_rgba(0, .25, 1, .3)
        self.ctx.new_path()
        y_high = optical_element.maximum_height
        for i, sphere in enumerate(spheres):
            # De cada esfera determinem el segment d'arc que cal dibuixar...
            y, z = sphere.position[1:]
            z_high = z + np.sign(optical_element.radii[i]) *\
                                     np.sqrt(sphere.radius ** 2 - y_high ** 2)
            # Angle dels extrems de la circumferència respecte el centre
            print(y_high/(z_high-z))
            phi_high = np.arctan2( y_high, z_high-z) + np.pi
            phi_low  = np.arctan2(-y_high, z_high-z) + np.pi

            phi_0 = min(phi_high, phi_low)
            phi_1 = max(phi_high, phi_low)
            xc, yc = self.transform(z, y)
            R = abs(sphere.radius * self.scale)

            # Podem ara pintar l'arc en qüestió...
            if optical_element.radii[i] > 0 :
                self.ctx.arc(xc, yc, R, phi_0, phi_1)
            else:
                self.ctx.arc(xc, yc, R, phi_1, phi_0)
        self.ctx.fill()


    def save_and_close(self):
        self.ctx.fill()
        self.surface.finish()
        self.surface.flush()
