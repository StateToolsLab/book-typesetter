// 実行のあと、InDesign に開いている文書の名前を出すだけ。閉じない。閉じるかどうかは人が決める。
var out = [];
for (var i = app.documents.length - 1; i >= 0; i--) {
  var d = app.documents[i];
  out.push(d.name + (d.saved ? '' : ' (未保存)'));
}
out.join(', ');
