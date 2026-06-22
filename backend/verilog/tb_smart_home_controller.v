`timescale 1ns/1ps

module tb_smart_home_controller;

    reg clk = 1'b0;
    reg reset = 1'b1;
    reg motion_sensor = 1'b0;
    reg light_sensor_dark = 1'b0;
    reg [7:0] temperature = 8'd25;
    reg door_open = 1'b0;
    reg security_mode = 1'b0;
    reg manual_override = 1'b0;
    reg manual_light = 1'b0;
    reg manual_fan = 1'b0;
    reg manual_socket = 1'b0;
    reg overcurrent = 1'b0;
    reg no_motion_timeout = 1'b0;

    wire [7:0] light_pwm;
    wire [7:0] fan_pwm;
    wire socket_relay;
    wire ac_relay;
    wire alarm;
    wire energy_saving;
    wire [1:0] state;

    smart_home_controller dut (
        .clk(clk),
        .reset(reset),
        .motion_sensor(motion_sensor),
        .light_sensor_dark(light_sensor_dark),
        .temperature(temperature),
        .door_open(door_open),
        .security_mode(security_mode),
        .manual_override(manual_override),
        .manual_light(manual_light),
        .manual_fan(manual_fan),
        .manual_socket(manual_socket),
        .overcurrent(overcurrent),
        .no_motion_timeout(no_motion_timeout),
        .light_pwm(light_pwm),
        .fan_pwm(fan_pwm),
        .socket_relay(socket_relay),
        .ac_relay(ac_relay),
        .alarm(alarm),
        .energy_saving(energy_saving),
        .state(state)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("smart_home_controller.vcd");
        $dumpvars(0, tb_smart_home_controller);

        #20 reset = 1'b0;

        // Case 1: dark room with motion turns light ON.
        #20 motion_sensor = 1'b1; light_sensor_dark = 1'b1; temperature = 8'd26;

        // Case 2: high temperature turns fan ON.
        #40 temperature = 8'd32;

        // Case 3: very high temperature turns AC relay ON.
        #40 temperature = 8'd36;

        // Case 4: manual override gets priority.
        #40 manual_override = 1'b1; manual_light = 1'b0; manual_fan = 1'b1; manual_socket = 1'b1;

        // Case 5: security mode with open door activates alarm.
        #40 manual_override = 1'b0; security_mode = 1'b1; door_open = 1'b1;

        // Case 6: overcurrent also activates alarm and forces relays OFF.
        #40 door_open = 1'b0; overcurrent = 1'b1;

        // Case 7: energy-saving timeout turns unnecessary outputs OFF.
        #40 overcurrent = 1'b0; security_mode = 1'b0; no_motion_timeout = 1'b1; motion_sensor = 1'b0;

        #80 $finish;
    end

    initial begin
        $monitor(
            "time=%0t state=%b light_pwm=%0d fan_pwm=%0d socket=%b ac=%b alarm=%b energy=%b",
            $time, state, light_pwm, fan_pwm, socket_relay, ac_relay, alarm, energy_saving
        );
    end

endmodule
