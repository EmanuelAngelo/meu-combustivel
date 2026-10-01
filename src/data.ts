export type Vehicle={id:number,type:string,brand:string,model:string,year:number,capacity:number,fuel:string,primary:boolean}
export type Station={id:number,name:string,address:string,city:string,state:string,lat:number,lng:number,price:number,air:'Gratuito'|'Pago'|'Não informado',updated:string}
export type Fill={id:number,vehicle:number,station:number,date:string,fuel:string,price:number,total:number,liters:number,km:number|null,full:boolean,payment:string,note:string}
export const initialVehicles:Vehicle[]=[{id:1,type:'Moto',brand:'Yamaha',model:'Fluo 125',year:2023,capacity:4.2,fuel:'Gasolina comum',primary:true}]
export const initialStations:Station[]=[
{id:1,name:'Posto Exemplo · Renascença',address:'Região do Renascença',city:'São Luís',state:'MA',lat:-2.5025,lng:-44.2896,price:6.20,air:'Gratuito',updated:'2026-10-01'},
{id:2,name:'Posto Exemplo · Cohama',address:'Região da Cohama',city:'São Luís',state:'MA',lat:-2.516,lng:-44.25,price:6.09,air:'Gratuito',updated:'2026-10-01'},
{id:3,name:'Posto Exemplo · Centro',address:'Região do Centro',city:'São Luís',state:'MA',lat:-2.529,lng:-44.30,price:6.39,air:'Pago',updated:'2026-10-01'},
{id:4,name:'Posto Exemplo · Calhau',address:'Região do Calhau',city:'São Luís',state:'MA',lat:-2.482,lng:-44.26,price:6.29,air:'Não informado',updated:'2026-10-01'}]
export const initialFills:Fill[]=[
{id:1,vehicle:1,station:1,date:'2026-09-28',fuel:'Gasolina comum',price:6.2,total:23.4,liters:3.774,km:4280,full:true,payment:'Pix',note:''},
{id:2,vehicle:1,station:2,date:'2026-09-23',fuel:'Gasolina comum',price:6.09,total:21.32,liters:3.5,km:4156,full:true,payment:'Pix',note:''},
{id:3,vehicle:1,station:4,date:'2026-09-17',fuel:'Gasolina comum',price:6.29,total:25.16,liters:4,km:4038,full:true,payment:'Débito',note:''}]
