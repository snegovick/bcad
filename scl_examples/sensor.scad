module us_sensor(tolerance=0) {
  color("green") translate([-45.5/2, -1.5, -20.5/2]) cube([45.5, 1.5, 20.5]);
  translate([-12.5,-1.5,0]) rotate([90,0,0]) color("gray") cylinder(d=16+tolerance, h=12, $fn=64);
  translate([12.5,-1.5,0]) rotate([90,0,0]) color("gray") cylinder(d=16+tolerance, h=12, $fn=64);
  start=3.81+2.54*2;
  for (x=[start:-2.54:-3.81]) {
    color("yellow") translate([x,0,0]) translate([-0.5, 2,-18]) cube([1,1,10]);
  }
  color([0.2,0.2,0.2]) translate([-3.81-1.5,-0,-9]) cube([3.81*2+2.54*2+3, 2, 2]);
}

us_sensor();
