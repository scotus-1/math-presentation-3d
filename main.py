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


SECTION_DIV = False;
SKIP_ANIM = True;

L1 = [230,-285,105]
L2 = [860,105,264]
CAM = [1000,0,0]
PLANE_POSITIONS = [[0,400,600], [0,400,0],[0,-400,0], [0,-400,600]]
P1 = [125, -350, 75]
P2 = [650, -25, 210]


def pointstr(array3d):
    return f"({array3d[0]},{array3d[1]},{array3d[2]})"


class Q1(ThreeDScene):
    def div(self, ovr=False):
        if SECTION_DIV:
            if ovr:
                self.next_section()                
            elif SKIP_ANIM:
                self.next_section(skip_animations=True)
        else:
            self.wait(1)

        
            
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
        self.div()

        # cross vectors together and then blink
        for index, plane in enumerate(frustum_planes):
            n = get_normal_vec(plane)
            x = MathTex(r"\times").next_to(n.get_start()).scale(1)
            self.add_fixed_orientation_mobjects(x)
            vl1 = vec_labels[index].copy()
            vl2 = vec_labels[(index+1) % 4].copy()
            self.add_fixed_orientation_mobjects(vl1, vl2)

            cross_anim = [Create(x), Transform(vl1, x), Transform(vl2, x), Flash(x)]
            
            dot = Dot3D(n.get_start()).set_opacity(0)
            self.play(*cross_anim)
            self.play(Transform(dot, n), FadeOut(x))
            self.play(plane.animate.set_opacity(0.75), FadeOut(dot), FadeOut(n), run_time=0.3)
            self.div()
        
        # fade out labels and frustum filled in planes
        anims = [FadeOut(p) for p in frustum_planes]
        [anims.append(FadeOut(l) for l in vec_labels)]
        self.play(*anims)
        self.div()

        #reanimate the previous line L but split into segments for hidden line
        l_left = ParametricFunction(
            lambda t: axes.coords_to_point(630* t + 230, 390* t -285, 162*t + 102),
            [-1,-1/6 + 0.005],
            dt=0.2
        )
        l_mid = ParametricFunction(
            lambda t: axes.coords_to_point(630* t + 230, 390* t -285, 162*t + 102),
            [-1/6,2/3 + 0.005],
            dt=0.2
        )
        l_right = ParametricFunction(
            lambda t: axes.coords_to_point(630* t + 230, 390* t -285, 162*t + 102),
            [2/3,1.5],
            dt=0.2
        )

        # define draw order
        self.add(l_mid)
        self.add(frustum_vecs[0], frustum_vecs[3])
        self.add(frustum_planes[2].set_opacity(0), frustum_planes[3].set_opacity(0))
        self.add(l_left, l_right)
        
        # add in para_eq
        para_eq_label.move_to(l_right.get_center() + OUT*0.2 + RIGHT*0.4).scale(0.8)
        label_cpy = para_eq_label.copy()
        self.add_fixed_orientation_mobjects(para_eq_label, label_cpy)

        self.play(FadeIn(l_left), FadeIn(l_mid), FadeIn(l_right), Write(para_eq_label), Write(label_cpy))
        self.div()

        # add labels
        pleft_label = Label(MathTex(r"2x - 5y = 2000"), box_config=box_config, label_config=label_config).move_to(frustum_planes[2].get_center() - OUT * 0.7).scale(0.8)
        pup_label = Label(MathTex(r"3x + 5z = 3000"), box_config=box_config, label_config=label_config).move_to(frustum_planes[3].get_center()).scale(0.8)

        self.add_fixed_orientation_mobjects(pleft_label, pup_label)
        
        self.play(frustum_planes[2].animate.set_opacity(0.75), frustum_planes[3].animate.set_opacity(0.75), Write(pleft_label), Write(pup_label))
        self.div()

        # combine para_eq_labels together 
        pleft_label_t = Label(MathTex(r"t = -\frac{1}{6}"), box_config=box_config, label_config=label_config).move_to(frustum_planes[2].get_center() - OUT * 0.5).scale(0.8)
        pup_label_t = Label(MathTex(r"t = \frac{2}{3}"), box_config=box_config, label_config=label_config).move_to(frustum_planes[3].get_center()).scale(0.8)
        self.add_fixed_orientation_mobjects(pleft_label_t, pup_label_t)
        self.play(FadeIn(pup_label_t),FadeIn(pleft_label_t), ReplacementTransform(pleft_label, pleft_label_t), ReplacementTransform(pup_label, pup_label_t), ReplacementTransform(para_eq_label, pleft_label_t), ReplacementTransform(label_cpy, pup_label_t))
        self.div()

        # Create dots at intersection points
        clipP1 = Dot3D(axes.c2p(*P1), color=GREEN, radius=0.02)
        clipP2 = Dot3D(axes.c2p(*P2), color=GREEN, radius=0.02)

        self.play(FadeOut(pleft_label_t, target_position=clipP1), FadeOut(pup_label_t, target_position=clipP2), GrowFromCenter(clipP1), GrowFromCenter(clipP2), Flash(clipP1), Flash(clipP2))
        self.div()

        # fade out the rest of the line and frustum
        anims = []
        for obj in self.get_top_level_mobjects():
            if isinstance(obj, Line3D):
                anims.append(Uncreate(obj))
        
        self.add(clipP1)
        self.add(clipP2)
        self.play(*[anims], FadeOut(l_left), FadeOut(l_right), FadeOut(frustum_planes[2]), FadeOut(frustum_planes[3]))
        self.div()

        # add labels for last points
        label1 = Label(MathTex(pointstr(P1)), box_config=box_config, label_config=label_config).next_to(clipP1, OUT).scale(0.65)
        label2 = Label(MathTex(pointstr(P2)), box_config=box_config, label_config=label_config).next_to(clipP2, OUT).scale(0.6)
        self.add_fixed_orientation_mobjects(label1, label2)
        self.play(Write(label1), Write(label2))
        self.div()

        # move camera back to original pos and finito
        self.move_camera(80 * DEGREES, 45*DEGREES, 0, frame_center=ORIGIN, zoom=1, 
                         added_anims=[clipP1.animate.scale(3), clipP2.animate.scale(3)])
        


        






# class Q1Part2(ThreeDScene):
#     def div(self, ovr=False):
#         if SECTION_DIV:
#             if ovr:
#                 self.next_section()                
#             elif SKIP_ANIM:
#                 self.next_section(skip_animations=True)
#         else:
#             self.wait(0.1)

#     def construct(self):
#         # make axes and axes labels and draw
#         axes = ThreeDAxes((-200, 1000, 100), (-1000, 1000, 100), (-1000, 1000,100))
        
#         labels = axes.get_axis_labels(
#             Text("x").scale(0.7), Text("y").scale(0.45), Text("z").scale(0.45)
#         )
        

#         # add plane
#         plane_positions = axes.coords_to_point(PLANE_POSITIONS)
#         plane = Polygon(*plane_positions, color=BLUE, fill_opacity=0)
#         # add frustum_vecs
#         frustum_vecs = [Arrow3D(axes.c2p(*CAM), vertice, base_radius=0.03, thickness=0.001, color=BLUE) for vertice in plane.get_vertices()]


#         self.add(axes)
#         self.add(labels)
#         self.add(plane)
#         self.add(*frustum_vecs)
        

#         # # this fixes the camera
#         self.next_section(skip_animations=False)
#         self.move_camera(90 * DEGREES, 0*DEGREES, zoom=2.5, frame_center=plane.get_center()) 
#         self.next_section()   


