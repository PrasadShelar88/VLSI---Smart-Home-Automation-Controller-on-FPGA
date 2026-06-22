`timescale 1ns/1ps

module smart_home_controller #(
    parameter TEMP_THRESHOLD = 8'd30
) (
    input  wire       clk,
    input  wire       reset,
    input  wire       motion_sensor,
    input  wire       light_sensor_dark,
    input  wire [7:0] temperature,
    input  wire       door_open,
    input  wire       security_mode,
    input  wire       manual_override,
    input  wire       manual_light,
    input  wire       manual_fan,
    input  wire       manual_socket,
    input  wire       overcurrent,
    input  wire       no_motion_timeout,
    output reg  [7:0] light_pwm,
    output reg  [7:0] fan_pwm,
    output reg        socket_relay,
    output reg        ac_relay,
    output reg        alarm,
    output reg        energy_saving,
    output reg  [1:0] state
);

    localparam S_AUTO        = 2'b00;
    localparam S_MANUAL      = 2'b01;
    localparam S_ALARM       = 2'b10;
    localparam S_ENERGY_SAVE = 2'b11;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            light_pwm     <= 8'd0;
            fan_pwm       <= 8'd0;
            socket_relay  <= 1'b0;
            ac_relay      <= 1'b0;
            alarm         <= 1'b0;
            energy_saving <= 1'b0;
            state         <= S_AUTO;
        end else begin
            light_pwm     <= 8'd0;
            fan_pwm       <= 8'd0;
            socket_relay  <= 1'b0;
            ac_relay      <= 1'b0;
            alarm         <= 1'b0;
            energy_saving <= 1'b0;
            state         <= S_AUTO;

            if (overcurrent) begin
                state     <= S_ALARM;
                alarm     <= 1'b1;
                light_pwm <= 8'd255;
            end else if (security_mode && door_open) begin
                state     <= S_ALARM;
                alarm     <= 1'b1;
                light_pwm <= 8'd255;
            end else if (manual_override) begin
                state        <= S_MANUAL;
                light_pwm    <= manual_light  ? 8'd255 : 8'd0;
                fan_pwm      <= manual_fan    ? 8'd220 : 8'd0;
                socket_relay <= manual_socket;
            end else if (no_motion_timeout) begin
                state         <= S_ENERGY_SAVE;
                energy_saving <= 1'b1;
                if (temperature >= TEMP_THRESHOLD)
                    fan_pwm <= 8'd120;
            end else begin
                if (motion_sensor && light_sensor_dark)
                    light_pwm <= 8'd220;
                else if (light_sensor_dark)
                    light_pwm <= 8'd80;

                if (temperature >= (TEMP_THRESHOLD + 8'd5)) begin
                    fan_pwm  <= 8'd255;
                    ac_relay <= 1'b1;
                end else if (temperature >= TEMP_THRESHOLD) begin
                    fan_pwm <= 8'd170;
                end

                socket_relay <= motion_sensor;
            end
        end
    end

endmodule
