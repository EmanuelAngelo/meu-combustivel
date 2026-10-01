import test from 'node:test';import assert from 'node:assert/strict';import {checkFuel,parseDecimal,normalizedName} from './domain.mjs';
test('conferência respeita litros com três casas e centavos',()=>assert.deepEqual(checkFuel('6,20','23,04','3,716'),{expected:23.04,difference:0,effective:23.04/3.716,consistent:true}));
test('divergência não é ocultada',()=>{const r=checkFuel('6.20','25','3.716');assert.equal(r.difference,1.96);assert.equal(r.consistent,false)});
test('campos inválidos não produzem resultados financeiros',()=>{for(const v of ['',0,-1,'3x',Infinity])assert.equal(checkFuel('6.20','23.04',v),null);assert.ok(Number.isNaN(parseDecimal('1,2,3')))});
test('nomes equivalentes ajudam a evitar duplicação',()=>assert.equal(normalizedName('  Posto São   Luís '),normalizedName('posto sao luis')));
