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
SKIP_ANIM = False;

L1 = [230,-285,105]
L2 = [860,105,264]
CAM = [1000,0,0]
PLANE_POSITIONS = [[0,400,600], [0,400,0],[0,-400,0], [0,-400,600]]
P1 = [125, -350, 75]
P2 = [650, -25, 210]
PROJP1 = [0,-400, 600/7]
PROJP2 = [0,-500/7,600]
box_config = {"fill_opacity": 0.25, "stroke_width": 0}
label_config = {"stroke_width":0}

def pointstr(array3d):
    return f"({array3d[0]},{array3d[1]},{array3d[2]})"


class Q1(ThreeDScene):
    def div(self, ovr=False):
        if SECTION_DIV:
            if ovr:
                self.next_section()                
            elif SKIP_ANIM:
                self.next_section(skip_animations=True)
            self.next_section() 
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
        


class Q2(ThreeDScene):
    def div(self, ovr=False):
        if SECTION_DIV:
            if ovr:
                self.next_section()                
            elif SKIP_ANIM:
                self.next_section(skip_animations=True)
            self.next_section() 
        else:
            self.wait(1)
    
    def construct(self):
        self.div()

        # make axes and axes labels and draw
        axes = ThreeDAxes((-200, 1000, 100), (-1000, 1000, 100), (-1000, 1000,100))
        labels = axes.get_axis_labels(
            Text("x").scale(0.7), Text("y").scale(0.45), Text("z").scale(0.45)
        )

        # add previous objects
        plane_positions = axes.coords_to_point(PLANE_POSITIONS)
        plane = Polygon(*plane_positions, color=BLUE, fill_opacity=1)
        
        self.add(axes, labels)
        self.add(plane)
        cam_dot = Dot3D(axes.c2p(*CAM), color=YELLOW, radius=0.08)
        cam_label = Label(MathTex(pointstr(CAM)), box_config=box_config, label_config=label_config).next_to(cam_dot, OUT).scale(0.6)
        
        clipP1 = Dot3D(axes.c2p(*P1), color=GREEN, radius=0.06)
        clipP2 = Dot3D(axes.c2p(*P2), color=GREEN, radius=0.06)
        label1 = Label(MathTex(pointstr(P1)), box_config=box_config, label_config=label_config).next_to(clipP1, OUT).scale(0.65)
        label2 = Label(MathTex(pointstr(P2)), box_config=box_config, label_config=label_config).next_to(clipP2, OUT).scale(0.6)
        l_mid = ParametricFunction(
            lambda t: axes.coords_to_point(630* t + 230, 390* t -285, 162*t + 102),
            [-1/6,2/3 + 0.005],
            dt=0.2
        )

        self.set_camera_orientation(80 * DEGREES, 45*DEGREES, 0)
        self.add_fixed_orientation_mobjects(label1, label2, cam_label)
        self.play(Create(axes), Create(labels), Create(plane), Create(cam_label), Create(clipP1), Create(clipP2), Create(label1), Create(label2), Create(l_mid), Create(cam_dot))
        self.div()

        self.move_camera(85*DEGREES, -40*DEGREES,0, zoom=1.3,
                         added_anims=[plane.animate.set_fill(opacity=0)])
        self.div()

        target_arrow = Arrow3D(cam_dot.get_center(), clipP1.get_center(), color=YELLOW)
        start_arrow = Line3D(axes.c2p(*CAM), axes.c2p(*CAM), color=YELLOW)
        self.play(Transform(start_arrow, target_arrow))
        self.div()

        p1 = axes.c2p(*PROJP1)
        p2 = axes.c2p(*PROJP2)
        l_proj_para = lambda t: (1 - t) * p1 + t * p2
        proj_dot = Dot3D(p1, color=YELLOW, radius=0.07)
        time = ValueTracker(0)
        proj_dot.add_updater(
            lambda m: m.move_to(l_proj_para(time.get_value()))
        )
        target_arrow = Arrow3D(axes.c2p(*CAM), axes.c2p(*P2), color=YELLOW)
        
        self.play(GrowFromCenter(proj_dot))
        self.play(Transform(start_arrow, target_arrow), time.animate.set_value(1), TracedPath(proj_dot, stroke_color=YELLOW, dissipating_time=0.2))
        self.div()        

        self.move_camera(2*DEGREES, -45*DEGREES, 0, zoom=1.0, added_anims=[FadeOut(label1), FadeOut(label2)])
        self.div()

        x_plane_label = Label(MathTex(r"x = 0"), box_config=box_config, label_config=label_config).next_to(plane, RIGHT).scale(1)
        v1_label = Label((r"\vec{v_{1}}"), box_config=box_config, label_config=label_config).next_to(target_arrow, OUT + UP).scale(1)
        self.add_fixed_orientation_mobjects(x_plane_label, v1_label)
        self.play(Write(x_plane_label), Write(v1_label))
        self.div()

        target_arrow = Arrow3D(axes.c2p(*CAM), proj_dot.get_center(), color=YELLOW)
        proj_dot_label = Label(MathTex(r"(0, \frac{-500}{7}, 600)"), box_config=box_config, label_config=label_config).next_to(proj_dot, OUT).scale(0.6)
        self.add_fixed_orientation_mobjects(proj_dot_label)
        self.play(Transform(start_arrow, target_arrow), ReplacementTransform(x_plane_label, v1_label), FadeOut(x_plane_label), FadeOut(v1_label), Write(proj_dot_label))
        self.div()

        proj_dot_2 = Dot3D(p1, color=YELLOW, radius=0.07) 
        start_arrow_2 = Arrow3D(axes.c2p(*CAM), axes.c2p(*CAM), color=YELLOW)
        target_arrow_2 = Arrow3D(axes.c2p(*CAM), p1, color=YELLOW)
        proj_dot_label_2 = Label(MathTex(r"(0, -400, \frac{600}{7})"), box_config=box_config, label_config=label_config).next_to(proj_dot_2, OUT).scale(0.6)
        self.add_fixed_orientation_mobjects(proj_dot_label_2)
        self.play(GrowFromCenter(proj_dot_2), Transform(start_arrow_2, target_arrow_2), Write(proj_dot_label_2))
        self.div()

        self.move_camera(88*DEGREES, -15*DEGREES,0, zoom=1.6, added_anims=[FadeOut(start_arrow), FadeOut(start_arrow_2)])
        self.div()

        l_proj = Line3D(axes.c2p(*PROJP1), axes.c2p(*PROJP2), color=YELLOW)
        self.play(GrowFromCenter(l_proj), FadeOut(proj_dot_label), FadeOut(proj_dot_label_2), FadeOut(cam_label))
        self.div(True)

        target_arrow = Arrow3D(cam_dot.get_center(), p1, color=RED)
        start_arrow = Line3D(axes.c2p(*CAM), axes.c2p(*CAM), color=RED)
        self.play(Transform(start_arrow, target_arrow))
        self.play(Flash(proj_dot_2))
        self.wait(0.25)
        # Rainbow colors as RGB
        rainbow_colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PINK]
        # ValueTracker from 0 to 1
        t_tracker = ValueTracker(0)
        # Function to interpolate between two colors
        def interpolate_colors(colors, t):
            n = len(colors) - 1
            # Map t in [0,1] to interval between colors
            t_scaled = t * n
            i = int(np.floor(t_scaled))
            frac = t_scaled - i
            if i >= n:
                return colors[-1]
            return interpolate_color(colors[i], colors[i+1], frac)
        
        target_arrow = Arrow3D(axes.c2p(*CAM), p2, color=RED)
        target_arrow.add_updater(
            lambda m: m.set_color(interpolate_colors(rainbow_colors, t_tracker.get_value()))
        )
        start_arrow.add_updater(
            lambda m: m.set_color(interpolate_colors(rainbow_colors, t_tracker.get_value()))
        )

        self.play(t_tracker.animate.set_value(1), Transform(start_arrow, target_arrow), run_time=2)
        self.play(Flash(proj_dot))











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


