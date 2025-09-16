from manim import *


def create_frustum_planes(plane: Polygon, center) -> list[Polygon]:
    frustum_planes = [];
    points = plane.get_vertices();
    for index, point in enumerate(points):
        frustum_planes.append(Polygon(center, point, points[(index + 1) % 4]))
    return frustum_planes

def get_normal_vec(plane: Polygon) -> Arrow3D:
    verts = plane.get_vertices();
    u = verts[0] - verts[1]
    v = verts[0] - verts[2]
    
    total = np.array([0.0,0.0,0.0])
    for p in verts:
        total += p
    total /= (3)

    direction = -np.cross(u,v) / 12
    return Arrow3D(total, direction, base_radius=0.03, thickness=0.005, color=RED)

SECTION_DIV = True;
SKIP_ANIM = True;

L1 = [230,-285,105]
L2 = [860,105,264]
CAM = [1000,0,0]
PLANE_POSITIONS = [[0,400,600], [0,400,0],[0,-400,0], [0,-400,600]]

def pointstr(array3d):
    return f"({array3d[0]},{array3d[1]},{array3d[2]})"

class ThreeD(ThreeDScene):
    def div(self, ovr=False):
        if SECTION_DIV:
            if ovr:
                self.next_section()                
            elif SKIP_ANIM:
                self.next_section(skip_animations=True)
        else:
            self.wait(0.1)

        
            
    def construct(self):
        self.div()

        # make axes and axes labels and draw
        axes = ThreeDAxes((-200, 1000, 100), (-1000, 1000, 100), (-1000, 1000,100))

        self.set_camera_orientation(80 * DEGREES, 45*DEGREES, 0)
        labels = axes.get_axis_labels(
            Text("x").scale(0.7), Text("y").scale(0.45), Text("z").scale(0.45)
        )

        self.play(Create(axes), Create(labels))
        self.div()
        

        # add plane
        plane_positions = axes.coords_to_point(PLANE_POSITIONS)
        plane = Polygon(*plane_positions, color=BLUE, fill_opacity=1)
        plane_center = plane.get_center()

        self.play(DrawBorderThenFill(plane))
        self.div()

        # add two points for line L with labels
        dotL1 = Dot3D(axes.c2p(*L1), color=RED, radius=0.08)
        dotL2 = Dot3D(axes.c2p(*L2), color=RED, radius=0.08)
        
        box_config = {"fill_opacity": 0.25, "stroke_width": 0}
        label_config = {"stroke_width":0}
        label1 = Label(MathTex(pointstr(L1)), box_config=box_config, label_config=label_config).next_to(dotL1, OUT).scale(0.7)
        label2 = Label(MathTex(pointstr(L2)), box_config=box_config, label_config=label_config).next_to(dotL2, OUT).scale(0.7)

        self.add_fixed_orientation_mobjects(label1)
        

        self.play(Create(dotL1), Create(label1))
        self.div()

        self.add_fixed_orientation_mobjects(label2)
        self.play(Create(dotL2), Create(label2))
        self.div()

        # connect line and disappear dots, combine label to create para line
        line = ParametricFunction(
            lambda t: axes.coords_to_point(630* t + 230, 390* t -285, 162*t + 102),
            [-1,1.5],
            dt=0.2
        )
        para_eq_label = Label(MathTex(r"\langle630t + 230, 390t - 285, 162t + 102\rangle"), box_config=box_config, label_config=label_config).next_to(line, OUT, buff=-0.2).scale(0.8)
        self.add_fixed_orientation_mobjects(para_eq_label)

        self.play(GrowFromCenter(line),FadeIn(para_eq_label), AnimationGroup(ReplacementTransform(label2, para_eq_label), ReplacementTransform(label1, para_eq_label)))
        self.div()
        
        # add camera point
        dot_cam = Dot3D(axes.c2p(*CAM), color=YELLOW, radius=0.08)
        cam_label = Label(MathTex(pointstr(CAM)), box_config=box_config, label_config=label_config).next_to(dot_cam, OUT).scale(0.6)
        self.add_fixed_orientation_mobjects(cam_label)

        self.play(Create(dot_cam), Create(cam_label))
        self.div()

        # move camera
        self.move_camera(90 * DEGREES, 0*DEGREES, zoom=2.5, frame_center=plane_center, 
                         added_anims=[plane.animate.set_fill(opacity=0), FadeOut(label1, label2, para_eq_label, dotL1, dotL2), cam_label.animate.next_to(dot_cam, OUT, buff= 0.05).scale(0.8)])
        self.div()
        
        # rm line for now
        self.play(FadeOut(line))
        self.div()

        # add points labels to then fuse with cam_center create frustum vecs
        plane_plabels = []
        for point in PLANE_POSITIONS:
            l = Label(MathTex(pointstr(point)), box_config=box_config, label_config=label_config).next_to(axes.c2p(*point), OUT).scale(0.7)
            self.add_fixed_orientation_mobjects(l)
            plane_plabels.append(l)
        
        self.play([Create(l) for l in plane_plabels])
        self.div()

        # fusion of pplabels + cam_center to draw frustmum vecs
        self.play([ReplacementTransform(l, cam_label) for l in plane_plabels])
        frustum_planes = create_frustum_planes(plane, axes.coords_to_point(*CAM))
        frustum_vecs = [Arrow3D(axes.c2p(*CAM), vertice, base_radius=0.03, thickness=0.001, color=BLUE) for vertice in plane.get_vertices()]
        vec_labels = [MathTex(fr"\vec{{v_{{{index+1}}}}}").next_to(vec.get_center(), OUT, buff=0.06) for index, vec in enumerate(frustum_vecs)]
        self.add_fixed_orientation_mobjects(*vec_labels)
        
        self.play(*[Transform(Line3D(axes.c2p(*CAM), axes.c2p(*CAM), color=BLUE), v) for v in frustum_vecs], *[FadeIn(l) for l in vec_labels], FadeOut(cam_label))
        self.div(ovr=True)

        # cross vectors together and then blink
        for index, plane in enumerate(frustum_planes):
            # if index != 2:
            #     continue
            n = get_normal_vec(plane)
            x = MathTex(r"\times").next_to(n.get_start()).scale(1)
            self.add_fixed_orientation_mobjects(x)
            vl1 = vec_labels[index].copy()
            vl2 = vec_labels[(index+1) % 4].copy()
            self.add_fixed_orientation_mobjects(vl1, vl2)

            cross_anim = [Create(x), Transform(vl1, x), Transform(vl2, x), Flash(x)]

            self.play(*cross_anim)
            self.play(Transform(Dot3D(n.get_start()).set_opacity(0), n), FadeOut(x))
            self.play(plane.animate.set_opacity(0.75), FadeOut(n), run_time=0.3)
        
        self.div(ovr=True)
        anims = [FadeOut(p) for p in frustum_planes]
        [anims.append(FadeTransform(v, Line3D(v.start, v.end,base_radius=0.03, thickness=0.001, color=BLUE))) for v in frustum_vecs]

        self.play(*anims)
            
            



        
        
        



