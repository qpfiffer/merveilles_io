/**
 * well-rng
 * A fast, pure javascript implementation of the WELL-1024a PRNG. Suitable for
 * use with Node.js or inside a browser with browserify. The output is limited
 * to 31 bits rather than 32, because javascript does not support unsigned ints
 *
 * Available under the terms of the MIT License. See LICENSE.
 * Copyright (c) 2013, Greg Malysa <gmalysa@stanford.edu>
 */

// WELL1024a has parameters:
// k=1024,w=32,r=32,p=0
// m1=3,m2=24,m3=10
// T0=M1, T1=M3(8), T2 = M3(-19), T3 = M3(-14)
// T4=M3(-11), T5=M3(-7), T6 = M3(-13), T7 = M0

/**
 * Constructor accepts an optional initial state vector. If this is not
 * supplied, then one will be generated automatically. The choice of state
 * vector is not particularly important (this is a strength of WELL) for
 * result quality, but specifying a vector is useful for obtaining repeatable
 * results
 * @param state 32-entry initial state vector
 */
function WELL(state) {
	if (!state)
		state = this.genstate();
	this.set_state(state, 0);
	this.next_bit = 32;
}

/**
 * Some constants used to produce various random numbers
 */
WELL.prototype.scale = 1 / (Math.pow(2, 31)-1);
WELL.prototype.positive_mask = Math.pow(2, 31)-1;
WELL.prototype.log2 = Math.log(2);

/**
 * Generate a random state vector using Math.random().
 * @return 32-entry initial state vector
 */
WELL.prototype.genstate = function() {
	var state = new Array(32);
	for (var i = 0; i < 32; ++i) {
		state[i] = 0 | (Math.random()*Math.pow(2, 32));
	}
	return state;
}

/**
 * Retrieve a copy of the internal state vector (you can modify this
 * without breaking the generator internals). You should retrieve the
 * state pointer separately if you intend to copy that as well.
 * @return 32-entry current state vector
 */
WELL.prototype.get_state = function() {
	return this._state.slice(0);
}

/**
 * Set the current state and state pointer to obtain a specific series of
 * values
 * @param state The 32-entry state vector to use, which should consist only of 32-bit ints
 * @param sp (optiona) The state pointer to use, which determines where we are in the state vector during PRNG operation
 */
WELL.prototype.set_state = function(state, sp) {
	if (state.length != 32)
		throw new TypeError('State vector is not 32 entries long!');

	this._n = sp || 0;
	this._state = state.slice(0);
}

/**
 * Retrieve a random integer from either 0 to 2^31-1 or -2^31 to 2^31-1, depending
 * on the argument given (none implies positive only)
 * @param incNeg (optional) If a truthy value, includes negative values in the output
 * @return int
 */
WELL.prototype.rand = function(incNeg) {
	var _state = this._state;
	var _n = this._n;

	// Algorithm pseudo-code from the paper
	// z0 = rot_p (v_r-2, v_r-1)
	// z1 = T0v_0 ^ T1V_m1
	// z2 = T2v_m2 ^ T3V_m3
	// z3 = z1 ^ z2
	// z4 = T4z0 ^ T5z1 ^ T6z2 ^ T7z3
	// vnext_r-1 = v_r-2 & m_p
	// for j = r-2 downto 2
	// 	vnext_j = v_j-1
	// vnext_1 = z3
	// vnext_0 = z4
	// output y = v_1 or v_0 (pick for convenience of implementation)

	var z0 = _state[(_n+31)&31];
	var v_m1 = _state[(_n+3)&31];
	var v_m2 = _state[(_n+24)&31];
	var v_m3 = _state[(_n+10)&31];
	var z1 = z0 ^ (v_m1 ^ (v_m1 >> 8));
	var z2 = v_m2 ^ (v_m2 << 19) ^ v_m3 ^ (v_m3 << 14);

	_state[_n] = (z1 ^ z2);
	this._n = _n = (_n + 31) & 31;
	_state[_n] = (z0 ^ (z0 << 11) ^ z1 ^ (z1 << 7) ^ z2 ^ (z2 << 13));

	return (incNeg ? _state[_n] : (_state[_n] & WELL.prototype.positive_mask));
}

/**
 * Retrieve a random float on the interval [0, 1) or (-1, 1) if the argument is
 * given
 * @param incNeg (optional) If a truthy value, includes negative values in output
 * @return float
 */
WELL.prototype.random = function(incNeg) {
	return WELL.prototype.rand.call(this, incNeg) * WELL.prototype.scale;
}

/**
 * Retrieve a random integer on the interval [a, b]
 * @return int
 */
WELL.prototype.randInt = function(a, b) {
	var dist = 1 + b - a;
	return (WELL.prototype.rand.call(this) % dist) + a;
}

/**
 * Obtains a small number of random bits (<32) amortizing the cost of running
 * the generator, where possible. This is must faster for generating powers of 2
 * than using randInt().
 * @param bits Number of bits to obtain
 * @return Random integer consisting of only the given number of bits
 */
WELL.prototype.randBits = function(bits) {
	var mask = (1 << bits) - 1;
	var unshift = 0;
	
	if (bits + this.next_bit <= 32) {
		unshift = this.next_bit;
		this.next_bit += bits;
	}
	else {
		this.bit_state = WELL.prototype.rand.call(this, true);
		this.next_bit = bits;
	}
	
	return (this.bit_state >> unshift) & mask;
}

module.exports = WELL;
