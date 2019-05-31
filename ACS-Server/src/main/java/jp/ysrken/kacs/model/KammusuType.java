package jp.ysrken.kacs.model;

public enum KammusuType {
    None,
    PT,
    DD,
    CL,
    CLT,
    CA,
    CAV,
    CVL,
    BC,
    BB,
    BBV,
    CV,
    AL,
    SS,
    SSV,
    AP,
    AV,
    LHA,
    ACV,
    AR,
    AS,
    TC,
    AO,
    CD;

    private final int value;

    private KammusuType() {
        this.value = 0;
    }

    private KammusuType(final int value) {
        this.value = value;
    }

    public static KammusuType of(int value) {
        if (value < 0)
            return KammusuType.None;
        return KammusuType.values()[value];
    }
}
