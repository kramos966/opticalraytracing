"""
OPTICAL ELEMENTS
"""
import numpy as np

class Ray(object):
    def __init__(self, position: np.ndarray, direction: np.ndarray, refractive_index: float):
        self.position = np.asarray(position, dtype=np.float32)
        self.direction = np.asarray(direction, dtype=np.float32)
        self.momentum = refractive_index * self.direction
        self.refractive_index = refractive_index

        self.trajectory = [self.position.copy()]

    def march(self, d: float):
        self.position += d*self.momentum/self.refractive_index
        self.trajectory.append(self.position.copy())

    def march_delta_z(self, delta_z: float):
        d = delta_z/self.direction[2]
        self.march(d)

class OpticalElement(object):
    def __init__(self, refractive_index):
        self.refractive_index = refractive_index

    def get_normal_vector(self, point):
        raise NotImplementedError("Function must be developed in children classes.")

    def refract_ray(self, ray: Ray, invert_normal=False):
        normal = self.get_normal_vector(ray.position)
        if invert_normal:
            normal[:] = -normal
        projection = np.dot(ray.momentum, normal)
        new_momentum = ray.momentum + normal * (\
                -projection + \
                np.sqrt(self.refractive_index ** 2 - ray.refractive_index ** 2 + \
                        projection ** 2))
        ray.momentum[:] = new_momentum
        ray.refractive_index = self.refractive_index + 0
        ray.direction[:] = new_momentum/self.refractive_index

class Sphere(OpticalElement):
    def __init__(self, position, radius, refractive_index):
        super().__init__(refractive_index)

        self.position = np.asarray(position, dtype=np.float32)
        self.radius = radius

    def ray_intersect(self, ray: Ray):
        """Intersecta l'esfera amb el raig donat. Retorna None si no hi ha
        interseccions."""
        ray_sphere_vector = ray.position - self.position
        scalar_product = np.dot(ray.direction, ray_sphere_vector)
        discriminant = scalar_product * scalar_product - \
                       np.dot(ray_sphere_vector, ray_sphere_vector) +\
                       self.radius * self.radius
        # No hi ha intersecció, sortim
        if discriminant < 0:
            return None
        arrelq = np.sqrt(discriminant)
        d1 = -scalar_product + arrelq
        d2 = -scalar_product - arrelq

        return d1, d2

    def get_normal_vector(self, point: np.ndarray) -> np.ndarray:
        """IMPORTANT: This assumes a point lying on the surface of the sphere!"""
        point_center_vector = point-self.position
        normalization_constant = np.sqrt(np.sum(point_center_vector*point_center_vector))
        return point_center_vector/normalization_constant

class SphericalLens(OpticalElement):
    def __init__(self, refractive_index: float, R1: float, R2: float, 
            position: np.ndarray, thickness: float):
        # Primera superfície còncava
        if R1 < 0:
            pass
        # Segona superfície còncava
        if R2 > 0:
            pass
        # Determining the distance between the virtual spheres by the lens thickness
        self.R1 = R1
        self.R2 = R2
        self.radii = [R1, R2]
        self.position = np.asarray(position)
        self.thickness = thickness
        self.sphere_distance = sphere_distance = abs(R1)+abs(R2)-thickness
        if sphere_distance <= 0:
            raise ValueError("Lents no es toquen...")
        # Pla d'intersecció respecte l'esfera 1
        self.z_intersect = (sphere_distance*sphere_distance + R1*R1 - R2*R2)/(2*sphere_distance)
        # Alçada màxima
        self.maximum_height = 1/(2*sphere_distance)*np.sqrt(
                                      ( abs(R1)+abs(R2)+sphere_distance)*\
                                      (-abs(R1)+abs(R2)+sphere_distance)*\
                                      ( abs(R1)+abs(R2)-sphere_distance)*\
                                      ( abs(R1)-abs(R2)+sphere_distance))
        # TODO: DEFINIM Z_INTERSECT COM A LA POSICIÓ DE LA LENT ---- CANVIA-HO!!!
        Sphere_1 = Sphere(self.position + np.asarray((0, 0, self.z_intersect)), 
                               abs(R1), refractive_index)
        Sphere_2 = Sphere(self.position - np.asarray((0, 0, self.z_intersect)), 
                               abs(R2), 1)
        self.Spheres = (Sphere_1, Sphere_2)

    def trace_ray(self, ray: Ray, debug=False):
        for i in range(2):
            sphere = self.Spheres[i]
            intersections = sphere.ray_intersect(ray)
            if not intersections:
                return None
            # Only interested in the nearest positive intersection
            d = min(intersections)
            if d < 0:
                d = max(intersections)
            if debug:
                print(d, ray.momentum)
            # March ray and intersect at the given surface
            ray.march(d)
            # Si el raig és més alt que l'esfera, talla'l
            # FIXME: Potser busca una altra estratègia?
            if ((abs(ray.position[:2]) > self.maximum_height).any()):
                return None
            # Invertim la normal només per a la primera esfera
            sphere.refract_ray(ray, invert_normal=not i)
            ray.refractive_index = sphere.refractive_index + 0

