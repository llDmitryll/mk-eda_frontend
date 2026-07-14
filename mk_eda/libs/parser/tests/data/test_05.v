module NegatedInputsBranching(A, B, Y1);
    input A;
    input B;
    output Y1;
    wire notA, notB, andGateOut, orGateOut;
    not (notA, A);
    not (notB, B);
    and (andGateOut, notA, notB);
    not (notAndGateOut, andGateOut);
    or (orGateOut, notA, notB);
    xor (Y1, notAndGateOut, orGateOut);
endmodule
