module inner_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h) {
  difference() {
    translate([3, inner_box_offset_y, inner_box_offset_z]) cube([10, box_inner_w, inner_h+0.1]);
    translate([-1.2-3,inner_box_offset_y+15,3]) rotate([0,45,0]) cube([10, box_w, 10]);
    translate([-7.2, 22, 0])  rotate([45,45,0]) cube([10,10,10]);
    translate([0,box_inner_w+1, 0]) rotate([0,0,45]) cube([10, 10, h+1]);
  }
}


is_top=true;
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


//translate([box_l,0,0])
mirror([1,0,0])
inner_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h);
inner_side_cutout(inner_box_offset_y, inner_box_offset_z, box_inner_w, box_w, h, inner_h);
