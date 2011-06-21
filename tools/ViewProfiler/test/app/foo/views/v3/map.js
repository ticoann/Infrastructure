function(doc) {
  var w = doc.small_int * doc.small_int;
  var x = doc.small_int * doc.big_int;
  var y = doc.big_int / doc.small_int;
  var z = doc.small_int * doc.big_int;
  var a = w * x * y * z;
  emit(a, doc.short_string);
}