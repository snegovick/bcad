module am_top_panel() {
  small_panel_l = 213;
  small_panel_h = 52;
  tolerance = 0.4;

  difference() {
    cube([small_panel_l, 1.8, small_panel_h]);
    translate([-3,2,-6.5]) rotate([90,0,0]) {
      //usb
      translate([166.5-tolerance, 41.5-tolerance, -1]) cube([13+tolerance*2, 12+tolerance*2, 10]);
      //switch
      translate([148.2-tolerance, 47.5-tolerance, -1]) cube([8+tolerance*2, 4+tolerance*2, 10]);
      //rj
      translate([125-tolerance, 38.8-tolerance, -1]) cube([13+tolerance*2, 15+tolerance*2, 10]);
    }
    translate([-3,2,-6.5+2.5]) rotate([90,0,0]) {
      translate([15.5-tolerance, 18.8-tolerance, -1]) cube([9.5+tolerance*2, 21+tolerance*2, 10]);
      translate([20.5, 15.3, -1]) cylinder(d=3.2, h=10, $fn=32);
      translate([20.5, 43.3, -1]) cylinder(d=3.2, h=10, $fn=32);
      translate([33.9-tolerance, 17.25-1.75-tolerance, -1]) cube([72.2+tolerance*2, 25+tolerance*2, 10]);

      
      translate([131.5, 13.8, -1]) cylinder(d=13.5, h=10, $fn=32);
      translate([152.25, 13.8, -1]) cylinder(d=13.5, h=10, $fn=32);
      translate([173, 13.8, -1]) cylinder(d=13.5, h=10, $fn=32);
      translate([198.5, 43.3, -1]) cylinder(d=3.2, h=10, $fn=32);
      translate([198.5, 15.3, -1]) cylinder(d=3.2, h=10, $fn=32);
      translate([194-tolerance, 18.8-tolerance, -1]) cube([9.5+tolerance*2, 21+tolerance*2, 10]);
      
      translate([121, 29.3, -1]) cylinder(d=3.2, h=10, $fn=32);
    }
  }
}

module am_bottom_panel() {
  small_panel_l = 213;
  small_panel_h = 52;
  tolerance = 0.4;
  small_panel_th = 1.8;
  cut_d = 8;

  difference() {
    cube([small_panel_l, small_panel_th, small_panel_h]);
    translate([121,-1,20]) cube([10,12,12]);
    translate([121+13, 3, 16]) rotate([90,0,0]) cylinder(d=2, h=10, $fn=32);

    offset1 = [small_panel_l/2-130/2, 0, small_panel_h/2-30/2];
    translate(offset1) rotate([90,0,0]) cylinder(d=cut_d, h=10, $fn=32, center =true);
    translate([offset1[0], offset1[1], 0]) translate([-cut_d/2, -1, -1]) cube([cut_d, 10, 12]);

    offset2 = [small_panel_l/2+130/2, 0, small_panel_h/2-30/2];
    translate(offset2) rotate([90,0,0]) cylinder(d=cut_d, h=10, $fn=32, center =true);
    translate([offset2[0], offset2[1], 0]) translate([-cut_d/2, -1, -1]) cube([cut_d, 10, 12]);

    offset3 = [small_panel_l/2+130/2, 0, small_panel_h/2+30/2];
    translate(offset3) rotate([90,0,0]) cylinder(d=cut_d, h=10, $fn=32, center =true);
    translate([offset3[0], offset3[1], 0]) translate([-cut_d/2, -1, small_panel_h-12+1]) cube([cut_d, 10, 12]);

    offset4 = [small_panel_l/2-130/2, 0, small_panel_h/2+30/2];
    translate(offset4) rotate([90,0,0]) cylinder(d=cut_d, h=10, $fn=32, center =true);
    translate([offset4[0], offset4[1], 0]) translate([-cut_d/2, -1, small_panel_h-12+1]) cube([cut_d, 10, 12]);

    //translate([50, -10, -1]) cube([200,100,100]);
    //translate([-1, -1, -1]) cube([30,10, 100]);

  }
}

module am_battery_drill_conductor() {
  difference() {
    translate([-15,-76,-26.0]) cube([110, 40, 2]);
    box_am_small();

    //stand-offs
    translate([89-97,-70,-30]) cylinder(d=3.5, h=10, $fn=32);
    translate([89-97+90,-70,-30]) cylinder(d=3.5, h=10, $fn=32);
    translate([89-97,-70+30,-30]) cylinder(d=3.5, h=10, $fn=32);
    translate([89-97+90,-70+30,-30]) cylinder(d=3.5, h=10, $fn=32);
    
    translate([38, -55, -30]) color("red") cube([10, 10, 10]);
  }

}

module inner_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h) {
  difference() {
    translate([3, inner_box_offset_y, inner_box_offset_z]) cube([10, box_inner_w, inner_h+0.1]);
    translate([-1.2-3,inner_box_offset_y+15,3]) rotate([0,45,0]) cube([10, box_w, 10]);
    translate([-7.2, 22, 0])  rotate([45,45,0]) cube([10,10,10]);
    translate([0,box_inner_w+1, 0]) rotate([0,0,45]) cube([10, 10, h+1]);
  }
}

module outter_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h) {
  union() {
    translate([-21,25,0]) rotate([0,45,0]) cube([20, box_w, 20]);
    translate([-27, 25, -6])  rotate([45,45,0]) cube([20,20,20]);
    translate([-7,box_inner_w, 0]) rotate([0,0,45]) cube([20, 20, h+1]);
  }
}

module box_am_small(is_top=true) {
  box_h_top = 30;
  box_h_bottom = 30;
  box_h = box_h_top + box_h_bottom;
  box_l = 235;
  box_w = 165;

  h = is_top ? box_h_top : box_h_bottom;

  box_inner_h_top = 27;
  box_inner_h_bottom = 27;
  box_inner_h = box_inner_h_top+box_inner_h_bottom;
  box_inner_l = 214;
  box_inner_w = 151;

  inner_h = is_top ? box_inner_h_top : box_inner_h_bottom;

  inner_box_offset_x = (box_l-box_inner_l)/2;
  inner_box_offset_y = (box_w-box_inner_w)/2;
  inner_box_offset_z_top = (box_h_top-box_inner_h_top);
  inner_box_offset_z_bottom = (box_h_bottom-box_inner_h_bottom);

  inner_box_offset_z = is_top ? inner_box_offset_z_top : inner_box_offset_z_bottom;

  translate([0,0,-inner_h])
  difference() {
    union() {
      translate([-box_l/2, -box_w/2, -inner_box_offset_z])
        difference() {
        cube([box_l, box_w, h]);
        translate([inner_box_offset_x, inner_box_offset_y, inner_box_offset_z]) cube([box_inner_l, box_inner_w, inner_h+0.1]);
        translate([inner_box_offset_x+3, -0.5, inner_box_offset_z_top+3]) cube([box_inner_l-6, box_w+1, h]);
    
        inner_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h);
        outter_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h);
    
        translate([box_l,0,0]) mirror([1,0,0]) inner_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h);
        translate([box_l,0,0]) mirror([1,0,0]) outter_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h);

        translate([inner_box_offset_x, inner_box_offset_y-2-1, inner_box_offset_z]) am_top_panel();
        translate([inner_box_offset_x, box_w-inner_box_offset_y+1, inner_box_offset_z]) am_top_panel();
      }
    
      translate([89, 70, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-89, 70, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([89, -70, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-89, -70, 0]) cylinder(d=6.5, h=5, $fn=32);

      translate([89, 60, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-89, 60, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([89, -60, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-89, -60, 0]) cylinder(d=6.5, h=5, $fn=32);

      translate([100.5, 44.5, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-100.5, 44.5, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([100.5, -44.5, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-100.5, -44.5, 0]) cylinder(d=6.5, h=5, $fn=32);

      translate([53.2, 44.5, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-53.2, 44.5, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([53.2, -44.5, 0]) cylinder(d=6.5, h=5, $fn=32);
      translate([-53.2, -44.5, 0]) cylinder(d=6.5, h=5, $fn=32);

      translate([box_inner_l/2+1.5, 52, 0]) translate([-3, -2.5, 0]) cube([4,5,21]);
      translate([box_inner_l/2+1.5, -52, 0]) translate([-3, -2.5, 0]) cube([4,5,21]);
      translate([-box_inner_l/2-1.5, 52, 0]) translate([-1, -2.5, 0]) cube([4,5,21]);
      translate([-box_inner_l/2-1.5, -52, 0]) translate([-1, -2.5, 0]) cube([4,5,21]);

      translate([45, 52, 0]) translate([-1.5, -2.5,0]) cube([3,5,2]);
      translate([-45, 52, 0]) translate([-1.5, -2.5,0]) cube([3,5,2]);
      translate([45, -52, 0]) translate([-1.5, -2.5,0]) cube([3,5,2]);
      translate([-45, -52, 0]) translate([-1.5, -2.5,0]) cube([3,5,2]);

      translate([box_inner_l/2+1.5, 52, 0]) translate([1, -0.5,2]) cube([5, 1, 19]);
      translate([box_inner_l/2+1.5, -52, 0]) translate([1, -0.5,2]) cube([5, 1, 19]);
      translate([-box_inner_l/2-1.5, 52, 0]) translate([-6, -0.5,2]) cube([5, 1, 19]);
      translate([-box_inner_l/2-1.5, -52, 0]) translate([-6, -0.5,2]) cube([5, 1, 19]);

    }
    translate([0,52,0]) translate([-box_inner_l/2-1.5, -1,0]) cube([box_inner_l+3, 2, h]);
    translate([0,-52,0]) translate([-box_inner_l/2-1.5, -1,0]) cube([box_inner_l+3, 2, h]);  
  }
}

box_am_small();
//translate([0,0,10]) rotate([0,180,0]) box_am_small();
//small_panel();
